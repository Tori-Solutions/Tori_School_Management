/** @odoo-module **/
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

class ToriDashboard extends Component {
    static template = "tori_school_management.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            stats: {},
            recentApplications: [],
            feeAlerts: [],
            announcements: [],
            pipeline: [],
            pipelineMax: 1,
            generatedOn: null,
            loading: true,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            const payload = await this.orm.call("tori.dashboard", "get_dashboard_payload", []);
            const pipeline = payload.pipeline || [];
            const pipelineMax = Math.max(1, ...pipeline.map((p) => p.count || 0));
            Object.assign(this.state, {
                stats: payload.stats || {},
                recentApplications: payload.recent_applications || [],
                feeAlerts: payload.fee_alerts || [],
                announcements: payload.announcements_today || [],
                pipeline,
                pipelineMax,
                generatedOn: payload.generated_on || null,
            });
        } catch (error) {
            this.notification.add("Unable to load dashboard data right now.", {
                type: "warning",
            });
        } finally {
            this.state.loading = false;
        }
    }

    stageBarWidth(count) {
        const base = this.state.pipelineMax ? (count / this.state.pipelineMax) * 100 : 0;
        return `${Math.max(12, Math.round(base))}%`;
    }

    getInitials(name) {
        const value = (name || "").trim();
        if (!value) {
            return "NA";
        }
        const tokens = value.split(/\s+/).slice(0, 2);
        return tokens.map((t) => t[0].toUpperCase()).join("");
    }

    stateBadgeClass(state) {
        if (state === "enrolled") {
            return "bg-success";
        }
        if (state === "confirm") {
            return "bg-primary";
        }
        if (state === "cancel") {
            return "bg-secondary";
        }
        return "bg-warning text-dark";
    }

    formatAmount(amount) {
        return new Intl.NumberFormat(undefined, {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2,
        }).format(amount || 0);
    }

    async openAction(xmlId, fallbackAction = null) {
        if (xmlId) {
            try {
                await this.action.doAction(xmlId);
                return;
            } catch (error) {
                // Fallback below.
            }
        }
        if (fallbackAction) {
            await this.action.doAction(fallbackAction);
            return;
        }
        this.notification.add("Unable to open this section.", { type: "warning" });
    }

    async openStudents() {
        await this.openAction(null, {
            type: "ir.actions.act_window",
            name: "Students",
            res_model: "res.partner",
            domain: [["is_student", "=", true]],
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async openApplications() {
        await this.openAction("tori_school_management.action_tori_student_application");
    }

    async openFaculty() {
        await this.openAction("hr.open_view_employee_list", {
            type: "ir.actions.act_window",
            name: "Faculty",
            res_model: "hr.employee",
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async openEnrollments() {
        await this.openAction("tori_school_management.action_tori_enrollment");
    }

    async openFees() {
        await this.openAction("tori_school_management.action_tori_fee_slip");
    }

    async openAttendance() {
        await this.openAction("tori_school_management.action_tori_attendance");
    }

    async openTimetable() {
        await this.openAction("tori_school_management.action_tori_timetable");
    }

    async openApplication(id) {
        if (!id) {
            return;
        }
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "tori.student.application",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("tori_school_dashboard", ToriDashboard);
