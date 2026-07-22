from django.core.management.base import BaseCommand
from users.models import Role, Department, Permission


class Command(BaseCommand):
    help = 'Seeds initial hospital roles, departments, and permissions for Kolak ERM.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding roles, departments, and permissions...")

        # 1. Standard Permissions
        permissions_data = [
            {"code": "patients.view", "name": "View Patient Records", "module": "patients"},
            {"code": "patients.create", "name": "Register Patient", "module": "patients"},
            {"code": "patients.edit", "name": "Edit Patient Info", "module": "patients"},
            {"code": "appointments.book", "name": "Book Appointment", "module": "appointments"},
            {"code": "appointments.manage_queue", "name": "Manage Queue", "module": "appointments"},
            {"code": "clinical.consultation", "name": "Perform Consultation", "module": "clinical"},
            {"code": "pharmacy.dispense", "name": "Dispense Medication", "module": "pharmacy"},
            {"code": "laboratory.manage_tests", "name": "Manage Lab Tests", "module": "laboratory"},
            {"code": "radiology.manage_imaging", "name": "Manage Imaging Requests", "module": "radiology"},
            {"code": "billing.manage_invoices", "name": "Manage Invoices & Payments", "module": "billing"},
            {"code": "users.manage_staff", "name": "Manage Staff & System Settings", "module": "users"},
        ]

        permission_objs = {}
        for pdata in permissions_data:
            perm, created = Permission.objects.get_or_create(
                code=pdata["code"],
                defaults={"name": pdata["name"], "module": pdata["module"]}
            )
            permission_objs[pdata["code"]] = perm
            if created:
                self.stdout.write(f"  + Created Permission: {pdata['code']}")

        # 2. Standard Hospital Roles
        roles_data = [
            {
                "code": "SUPER_ADMIN",
                "name": "System Administrator",
                "is_system": True,
                "perms": list(permission_objs.keys())
            },
            {
                "code": "HOSPITAL_ADMIN",
                "name": "Hospital Administrator",
                "is_system": True,
                "perms": ["patients.view", "users.manage_staff", "billing.manage_invoices"]
            },
            {
                "code": "DOCTOR",
                "name": "Doctor / Specialist",
                "is_system": True,
                "perms": ["patients.view", "appointments.book", "appointments.manage_queue", "clinical.consultation", "laboratory.manage_tests", "radiology.manage_imaging"]
            },
            {
                "code": "NURSE",
                "name": "Nurse / Triage Officer",
                "is_system": True,
                "perms": ["patients.view", "patients.create", "appointments.manage_queue", "clinical.consultation"]
            },
            {
                "code": "FRONT_DESK",
                "name": "Front Desk / Receptionist",
                "is_system": True,
                "perms": ["patients.view", "patients.create", "patients.edit", "appointments.book", "appointments.manage_queue"]
            },
            {
                "code": "PHARMACIST",
                "name": "Pharmacist",
                "is_system": True,
                "perms": ["patients.view", "pharmacy.dispense"]
            },
            {
                "code": "LAB_TECH",
                "name": "Lab Technician",
                "is_system": True,
                "perms": ["patients.view", "laboratory.manage_tests"]
            },
            {
                "code": "RADIOLOGIST",
                "name": "Radiologist",
                "is_system": True,
                "perms": ["patients.view", "radiology.manage_imaging"]
            },
            {
                "code": "BILLING_OFFICER",
                "name": "Billing Officer / Cashier",
                "is_system": True,
                "perms": ["patients.view", "billing.manage_invoices"]
            },
            {
                "code": "RECORD_OFFICER",
                "name": "Medical Records Officer",
                "is_system": True,
                "perms": ["patients.view", "patients.create", "patients.edit"]
            },
        ]

        for rdata in roles_data:
            role, created = Role.objects.get_or_create(
                code=rdata["code"],
                defaults={"name": rdata["name"], "is_system": rdata["is_system"]}
            )
            role_perms = [permission_objs[code] for code in rdata["perms"] if code in permission_objs]
            role.permissions.set(role_perms)
            if created:
                self.stdout.write(f"  + Created Role: {rdata['name']} ({rdata['code']})")

        # 3. Standard Hospital Departments
        departments_data = [
            {"name": "General Medicine (OPD)", "description": "Outpatient consultation and general medical care"},
            {"name": "Obstetrics & Gynecology (OB/GYN)", "description": "Maternal, fetal, and women's healthcare"},
            {"name": "Pediatrics", "description": "Child health and medical care"},
            {"name": "General Surgery", "description": "Surgical procedures and post-op management"},
            {"name": "Emergency & Triage (Casualty)", "description": "24/7 acute trauma and emergency triage"},
            {"name": "Pharmacy", "description": "Medication procurement, storage, and dispensing"},
            {"name": "Laboratory & Pathology", "description": "Diagnostic lab tests and pathology services"},
            {"name": "Radiology & Diagnostic Imaging", "description": "X-Ray, Ultrasound, CT Scan, and MRI services"},
            {"name": "Nursing & Wards", "description": "Inpatient ward care, vitals monitoring, nursing care"},
            {"name": "Billing & Accounts", "description": "Patient invoicing, cashiering, and HMO claims management"},
            {"name": "Hospital Administration", "description": "Executive management, HR, IT, and hospital operations"},
        ]

        for ddata in departments_data:
            dept, created = Department.objects.get_or_create(
                name=ddata["name"],
                defaults={"description": ddata["description"]}
            )
            if created:
                self.stdout.write(f"  + Created Department: {ddata['name']}")

        self.stdout.write(self.style.SUCCESS("Successfully seeded roles, permissions, and departments!"))
