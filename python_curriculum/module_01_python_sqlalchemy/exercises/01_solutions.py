# =============================================================================
# MODULE 1: SOLUTIONS
# =============================================================================

from datetime import date
from sqlalchemy import select, update, func, and_, or_, not_
from module_01_python_sqlalchemy.setup_and_models import (  # type: ignore
    SessionLocal, Customer, Account, Transaction, Branch,
    Employee, Loan, AccountTypeEnum, LoanStatusEnum
)


def exercise_1():
    with SessionLocal() as session:
        stmt = (
            select(
                Customer.customer_id,
                Customer.first_name,
                Customer.last_name,
                Customer.email,
                Customer.state,
            )
            .where(Customer.is_active == True)
            .order_by(Customer.last_name, Customer.first_name)
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(row)
        return rows


def exercise_2():
    with SessionLocal() as session:
        stmt = (
            select(Account.account_id, Account.account_number, Account.balance)
            .where(
                and_(
                    Account.account_type == AccountTypeEnum.savings,
                    Account.balance > 20000,
                )
            )
            .order_by(Account.balance.desc())
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(row)
        return rows


def exercise_3() -> int:
    with SessionLocal() as session:
        stmt = (
            select(func.count())
            .select_from(Customer)
            .where(Customer.credit_score > 720)
        )
        count = session.execute(stmt).scalar()
        print(f"Customers with credit score > 720: {count}")
        return count


def exercise_4():
    with SessionLocal() as session:
        stmt = (
            select(Employee)
            .where(
                and_(
                    Employee.hire_date > date(2020, 1, 1),
                    Employee.is_active == True,
                )
            )
            .order_by(Employee.hire_date)
        )
        employees = session.execute(stmt).scalars().all()
        for e in employees:
            print(f"{e.first_name} {e.last_name}  Hired={e.hire_date}")
        return employees


def exercise_5():
    with SessionLocal() as session:
        # Insert
        test_customer = Customer(
            first_name    = "Test",
            last_name     = "User",
            email         = f"test.user.{date.today().isoformat()}@example.com",
            date_of_birth = date(1990, 1, 1),
            ssn_last4     = "9999",
            address_line1 = "1 Test Lane",
            city          = "Springfield",
            state         = "IL",
            zip_code      = "62701",
            credit_score  = 700,
            joined_date   = date.today(),
            is_active     = True,
        )
        session.add(test_customer)
        session.commit()
        session.refresh(test_customer)
        new_id = test_customer.customer_id
        print(f"Inserted customer ID={new_id}")

        # Soft-delete
        stmt = (
            update(Customer)
            .where(Customer.customer_id == new_id)
            .values(is_active=False)
        )
        session.execute(stmt)
        session.commit()
        print(f"Soft-deleted customer ID={new_id}")


def exercise_6():
    with SessionLocal() as session:
        stmt = (
            select(
                Loan.loan_id,
                Loan.customer_id,
                Loan.loan_type,
                Loan.status,
                Loan.remaining_balance,
            )
            .where(
                Loan.status.in_([LoanStatusEnum.delinquent, LoanStatusEnum.defaulted])
            )
            .order_by(Loan.remaining_balance.desc())
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(row)
        return rows


def exercise_7():
    with SessionLocal() as session:
        stmt = (
            select(Customer.first_name, Customer.last_name, Customer.email)
            .where(
                not_(
                    or_(
                        Customer.email.ilike("%@gmail.com"),
                        Customer.email.ilike("%@yahoo.com"),
                    )
                )
            )
            .order_by(Customer.last_name)
        )
        rows = session.execute(stmt).all()
        for row in rows:
            print(row)
        return rows


if __name__ == "__main__":
    print("Exercise 1:"); exercise_1()
    print("\nExercise 2:"); exercise_2()
    print("\nExercise 3 (count):", exercise_3())
    print("\nExercise 4:"); exercise_4()
    print("\nExercise 5:"); exercise_5()
    print("\nExercise 6:"); exercise_6()
    print("\nExercise 7:"); exercise_7()
