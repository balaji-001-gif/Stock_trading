# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class NAVPeriod(Document):
    """Multi-period NAV tracking with return calculations."""

    def validate(self):
        self.calculate_period_return()
        self.calculate_excess_return()

    def calculate_period_return(self):
        if self.nav_at_start and self.nav_at_start > 0:
            self.period_return = flt(self.nav_at_end) - flt(self.nav_at_start)
            self.period_return_percentage = (
                flt(self.period_return) / flt(self.nav_at_start)
            ) * 100

    def calculate_excess_return(self):
        if self.period_return_percentage is not None and self.benchmark_return is not None:
            self.excess_return = flt(self.period_return_percentage) - flt(self.benchmark_return)
