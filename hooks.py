import logging

_logger = logging.getLogger(__name__)


def uninstall_hook(env):
    """Clean up automation artefacts created by the module."""
    # Deactivate crons owned by this module
    crons = env['ir.cron'].search([
        ('cron_name', 'ilike', 'tori_school'),
    ])
    if crons:
        crons.write({'active': False})
        _logger.info("Deactivated %d tori_school cron(s).", len(crons))

    # Remove base.automation records owned by this module
    automations = env['base.automation'].search([
        ('action_server_ids.model_id.model', 'ilike', 'tori.'),
    ])
    if automations:
        automations.unlink()
        _logger.info("Removed %d tori_school automation(s).", len(automations))
