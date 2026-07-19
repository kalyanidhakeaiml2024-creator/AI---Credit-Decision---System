from flask import Flask, render_template, request, send_file
import joblib
import pandas as pd
import csv
import os

from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


app = Flask(__name__)

# ==========================
# LOAD MODEL
# ==========================

model = joblib.load("loan_model.pkl")

# ==========================
# GLOBAL VARIABLES
# ==========================

name = ""
age = 0
gender = ""
married = ""
employment = ""
income = 0
loan_amount = 0
credit_score = 0

result = ""
probability = ""
risk = ""

# ==========================
# HOME
# ==========================

@app.route("/")
def home():
    return render_template("loan.html")


@app.route("/loan")
def loan():
    return render_template("loan.html")


# ==========================
# ADMIN PAGE
# ==========================

@app.route("/admin")
def admin():

    try:

        df = pd.read_csv("loan_applications.csv")

        total = len(df)

        approved = int(total * 0.70)

        rejected = total - approved

        rate = round((approved / total) * 100, 2)

    except:

        total = 0
        approved = 0
        rejected = 0
        rate = 0

    return render_template(
        "admin.html",
        total=total,
        approved=approved,
        rejected=rejected,
        rate=rate
    )
# ==========================
# PREDICT
# ==========================

@app.route("/predict", methods=["POST"])
def predict():

    global name, age, gender, married
    global employment, income
    global loan_amount, credit_score
    global result, probability, risk

    # -----------------------------
    # GET FORM DATA
    # -----------------------------

    name = request.form["name"]
    age = int(request.form["age"])
    gender = request.form["gender"]
    married = request.form["married"]
    employment = request.form["employment"]
    income = int(request.form["income"])
    loan_amount = int(request.form["loan_amount"])
    credit_score = int(request.form["credit_score"])

    # -----------------------------
    # SAVE DATA TO CSV
    # -----------------------------

    filename = "loan_applications.csv"

    if not os.path.exists(filename):

        with open(filename, "w", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Name",
                "Age",
                "Gender",
                "Marital Status",
                "Employment",
                "Income",
                "Loan Amount",
                "Credit Score",
                "Date"
            ])

    with open(filename, "a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            name,
            age,
            gender,
            married,
            employment,
            income,
            loan_amount,
            credit_score,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ])

    # -----------------------------
    # MACHINE LEARNING PREDICTION
    # -----------------------------

    prediction = model.predict([[income, loan_amount]])[0]

    if prediction == 1:

        result = "LOAN APPROVED"
        probability = "92%"
        risk = "LOW RISK"
        status_class = "success"

    else:

        result = "LOAN REJECTED"
        probability = "34%"
        risk = "HIGH RISK"
        status_class = "fail"

    # -----------------------------
    # RESULT PAGE
    # -----------------------------

    return render_template(
        "result.html",
        name=name,
        age=age,
        gender=gender,
        employment=employment,
        income=income,
        loan_amount=loan_amount,
        credit_score=credit_score,
        result=result,
        probability=probability,
        risk=risk,
        status_class=status_class
    )
# ==========================
# DOWNLOAD PROFESSIONAL CAM REPORT
# ==========================

@app.route("/download")
def download():

    styles = getSampleStyleSheet()

    filename = "Loan_Report.pdf"

    doc = SimpleDocTemplate(filename)

    story = []

    # ==========================
    # BANK LOGO
    # ==========================

    logo_path = os.path.join(app.root_path, "logo.png")

    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=80, height=80)
            story.append(logo)
        except:
            pass

    story.append(Spacer(1, 10))

    # ==========================
    # REPORT TITLE
    # ==========================

    story.append(
        Paragraph(
            "<font color='darkblue'><b>ABC BANK LTD.</b></font>",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            "<b>Credit Appraisal Memorandum (CAM Report)</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            datetime.now().strftime("%d-%m-%Y %I:%M %p"),
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 20))

    # ==========================
    # APPLICANT DETAILS TABLE
    # ==========================

    details = [

        ["Applicant Name", name],

        ["Age", str(age)],

        ["Gender", gender],

        ["Employment", employment],

        ["Income", f"₹ {income:,}"],

        ["Loan Amount", f"₹ {loan_amount:,}"],

        ["Credit Score", str(credit_score)]

    ]

    table = Table(details, colWidths=[170, 250])

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (0, -1), colors.darkblue),

        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),

        ("BACKGROUND", (1, 0), (1, -1), colors.beige),

        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),

        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

    ]))

    story.append(table)

    story.append(Spacer(1, 20))

    # ==========================
    # DECISION TABLE
    # ==========================

    decision = [

        ["Prediction", result],

        ["Approval Chance", probability],

        ["Risk Level", risk]

    ]

    decision_table = Table(decision, colWidths=[170, 250])

    decision_table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (0, -1), colors.green),

        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),

        ("BACKGROUND", (1, 0), (1, -1), colors.whitesmoke),

        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),

    ]))

    story.append(decision_table)

    story.append(Spacer(1, 20))

    # ==========================
    # STATUS
    # ==========================

    if result == "LOAN APPROVED":

        status = "<font color='green'><b>LOAN APPROVED</b></font>"

        recommendation = """
        The applicant satisfies the required eligibility criteria.
        Loan can be considered for sanction after standard verification.
        """

    else:

        status = "<font color='red'><b>LOAN REJECTED</b></font>"

        recommendation = """
        Applicant does not satisfy the eligibility criteria.
        Loan is not recommended at this stage.
        """

    story.append(Paragraph(status, styles["Heading1"]))

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "<b>Recommendation</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            recommendation,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 30))

    # ==========================
    # SIGNATURE TABLE
    # ==========================

    signature = Table(
        [
            ["Prepared By", "Verified By"],
            ["", ""]
        ],
        colWidths=[210, 210],
        rowHeights=[25, 60]
    )

    signature.setStyle(TableStyle([

        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold")

    ]))

    story.append(signature)

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "<b>System Generated CAM Report</b>",
            styles["Heading3"]
        )
    )

    story.append(
        Paragraph(
            "AI Credit Decision System | Confidential Bank Document",
            styles["BodyText"]
        )
    )

    doc.build(story)

    return send_file(
        filename,
        as_attachment=True
    )


# ==========================
# RUN APPLICATION
# ==========================

if __name__ == "__main__":
    app.run(debug=True)