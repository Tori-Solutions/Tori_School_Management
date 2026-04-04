"""Pre-migration: add currency_id columns for Float → Monetary conversion."""
import logging

_logger = logging.getLogger(__name__)

TABLES = [
    'tori_fee_structure',
    'tori_fee_element',
    'tori_fee_slip',
    'tori_scholarship',
]


def migrate(cr, version):
    if not version:
        return

    # Find BDT currency (Bangladeshi Taka) for default backfill
    cr.execute("SELECT id FROM res_currency WHERE name = 'BDT' LIMIT 1")
    row = cr.fetchone()
    if not row:
        _logger.warning("BDT currency not found; skipping currency_id backfill.")
        return
    bdt_id = row[0]

    for table in TABLES:
        cr.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = %s AND column_name = 'currency_id'",
            (table,),
        )
        if cr.fetchone():
            _logger.info("Column currency_id already exists on %s, skipping.", table)
            continue
        _logger.info("Adding currency_id to %s and backfilling with BDT (%s).", table, bdt_id)
        cr.execute(f'ALTER TABLE "{table}" ADD COLUMN currency_id integer')
        cr.execute(f'UPDATE "{table}" SET currency_id = %s WHERE currency_id IS NULL', (bdt_id,))
