# StudentName: Luciana Queiroz Nascimento
# StudentID: 2410060
# Date: 29/04/2025


from fastapi import FastAPI, HTTPException
import pymysql
import datetime


app = FastAPI()


connection = pymysql.connect(
    host="localhost",
    user="atm_user",
    password="123456",
    database="atm_db",
    port=3307
)

cursor = connection.cursor()


@app.post("/transactions/")
def add_transaction(trans_type: str, amount: float):
    try:
        if trans_type not in ["deposit", "withdraw"]:
            raise HTTPException(status_code=400, detail="Invalid transaction type. Use 'deposit' or 'withdraw'.")
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than zero, try again")

        if trans_type == "withdraw":
            cursor.execute("SELECT SUM(transaction_amount) FROM transactions")
            result = cursor.fetchone()
            current_balance = result[0] if result[0] else 0
            if amount > current_balance:
                raise HTTPException(status_code=400, detail="Insufficient funds for this withdrawal, try another amount.")

        sql = "INSERT INTO transactions (transaction_type, transaction_amount, transaction_date) VALUES (%s, %s, %s)"
        values = (trans_type, amount if trans_type == "deposit" else -amount, datetime.datetime.now())
        cursor.execute(sql, values)
        connection.commit()
        return {"message": f"Success! Your {trans_type} of ${amount:.2f} was completed."}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error while processing your transaction, try again.")

@app.get("/balance/")
def get_balance():
    try:
        cursor.execute("SELECT SUM(transaction_amount) FROM transactions")
        result = cursor.fetchone()
        balance = result[0] if result[0] else 0
        return {"balance": balance}
    except Exception:
        raise HTTPException(status_code=500, detail="Error, We were unable to check your balance, try again.")

@app.get("/transactions/")
def get_history():
    try:
        cursor.execute("SELECT transaction_type, transaction_amount, transaction_date FROM transactions ORDER BY transaction_date")
        results = cursor.fetchall()
        history = [
            {"type": row[0], "amount": row[1], "date": row[2].strftime("%Y-%m-%d %H:%M:%S")} for row in results
        ]
        return {"history": history}
    except Exception:
        raise HTTPException(status_code=500, detail="Error, We were unable to check your history, try again.")


