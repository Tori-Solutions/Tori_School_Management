/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * D6: Barcode scanner scoped to tori.student.attendance views only.
 * Does NOT intercept scans on product forms, vendor bills, stock moves, etc.
 */

const ATTENDANCE_MODEL = "tori.student.attendance";

const toriAttendanceBarcodeService = {
    dependencies: ["rpc", "notification", "action"],
    start(env, { rpc, notification, action }) {
        // Listen to global barcode scans but only act when on attendance model
        document.addEventListener("keydown", (ev) => {
            // Odoo web barcode service handles the low-level scanning;
            // we only hook into the global event flow when needed.
        });

        env.bus.addEventListener("BARCODE_SCANNED", async (ev) => {
            // Guard: only handle when current action targets attendance model
            const currentAction = action.currentController;
            if (
                !currentAction ||
                !currentAction.action ||
                currentAction.action.res_model !== ATTENDANCE_MODEL
            ) {
                return; // Not on attendance — let default behavior continue
            }

            const barcode = ev.detail;
            try {
                const result = await rpc("/edu/attendance/scan", {
                    barcode,
                    method: "barcode",
                });
                if (result && result.success) {
                    notification.add(result.message || "Attendance marked.", {
                        type: "success",
                        title: "Attendance",
                    });
                } else {
                    notification.add(
                        (result && result.message) || "Scan failed.",
                        { type: "warning", title: "Attendance" }
                    );
                }
            } catch {
                notification.add("Scanner error. Please try again.", {
                    type: "danger",
                });
            }
        });
    },
};

registry
    .category("services")
    .add("tori_school_barcode_attendance", toriAttendanceBarcodeService);

