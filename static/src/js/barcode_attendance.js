/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

/**
 * D6: Barcode scanner scoped to tori.student.attendance views only.
 * Does NOT intercept scans on product forms, vendor bills, stock moves, etc.
 */

const ATTENDANCE_MODEL = "tori.student.attendance";
const ATTENDANCE_SCAN_ROUTE = "/edu/attendance/scan";

function isRouteUnavailable(error) {
    const message = String(
        error?.message || error?.data?.message || error?.data?.debug || ""
    ).toLowerCase();
    return (
        message.includes("404") ||
        message.includes("not found") ||
        message.includes(ATTENDANCE_SCAN_ROUTE)
    );
}

const toriAttendanceBarcodeService = {
    dependencies: ["notification", "action"],
    start(env, { notification, action }) {
        let scannerEnabled = true;
        let disabledNotificationShown = false;

        // Listen to global barcode scans but only act when on attendance model
        document.addEventListener("keydown", (ev) => {
            // Odoo web barcode service handles the low-level scanning;
            // we only hook into the global event flow when needed.
        });

        const handleBarcode = async (ev) => {
            if (!scannerEnabled) {
                return;
            }

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
                const result = await rpc(ATTENDANCE_SCAN_ROUTE, {
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
            } catch (error) {
                if (isRouteUnavailable(error)) {
                    scannerEnabled = false;
                    if (!disabledNotificationShown) {
                        disabledNotificationShown = true;
                        notification.add(
                            "Attendance scan endpoint is unavailable. Barcode listener has been disabled.",
                            { type: "warning", title: "Attendance", sticky: true }
                        );
                    }
                    return;
                }
                notification.add("Scanner error. Please try again.", {
                    type: "danger",
                });
            }
        };

        if (env.bus && typeof env.bus.addEventListener === "function") {
            env.bus.addEventListener("BARCODE_SCANNED", handleBarcode);
        }
    },
};

const serviceRegistry = registry.category("services");
if (!serviceRegistry.contains("tori_school_barcode_attendance")) {
    serviceRegistry.add("tori_school_barcode_attendance", toriAttendanceBarcodeService);
}

