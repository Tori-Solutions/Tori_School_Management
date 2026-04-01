/** @odoo-module **/

import { registry } from "@web/core/registry";
import { BarcodeScanner } from "@web/core/barcode/barcode_scanner";

const schoolAttendanceScanner = {
    start(env) {
        const scanner = new BarcodeScanner({ env });
        scanner.addListener(async (barcode) => {
            await env.services.rpc("/edu/attendance/scan", {
                barcode,
                method: "barcode",
            });
        });
    },
};

registry.category("services").add("tori_school_barcode_attendance", schoolAttendanceScanner);

