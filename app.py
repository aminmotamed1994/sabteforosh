import streamlit as st
import pandas as pd
import os
from datetime import datetime

# تنظیمات صفحه
st.set_page_config(page_title="سامانه فروش طلافروشی", page_icon="💰", layout="wide")

# ایجاد پوشه‌ها برای ذخیره اطلاعات
os.makedirs("images", exist_ok=True)
os.makedirs("data", exist_ok=True)
CSV_FILE = "data/sales_records.csv"

USERS = ["امین (مدیر)", "سلمان (حسابدار)", "رئوف (فروشنده ۳)"]
BANKS = ["بانک ملت", "بانک ملی", "بانک صادرات", "بانک تجارت", "بانک پاسارگاد"]

st.title("💰 سامانه ثبت فروش طلافروشی")
st.markdown("##### کاربر گرامی، لطفاً اطلاعات فروش را با دقت وارد کنید.")

invoice_id = datetime.now().strftime("%Y%m%d%H%M%S")

# بخش ۱: اطلاعات پایه
st.header("۱. اطلاعات فروشنده و جنس")
col1, col2 = st.columns(2)
with col1:
    user = st.selectbox("نام کاربر ثبت کننده:", USERS)
    item_type = st.text_input("نوع جنس فروخته شده (مثلا: النگه، زنجیر، سکه)")
with col2:
    item_desc = st.text_area("توضیحات جنس")
    weight = st.number_input("وزن محصول (گرم)", min_value=0.0, format="%.2f")

# بخش ۲: وضعیت جنس و اجرت
st.header("۲. وضعیت محصول و اجرت")
col3, col4 = st.columns(2)
with col3:
    condition = st.radio("وضعیت محصول:", ["نو", "کارکرده"])
with col4:
    making_charge = 0.0
    if condition == "نو":
        making_charge = st.number_input("اجرت (تومان)", min_value=0)

final_price = st.number_input("مبلغ نهایی فروش (تومان)", min_value=0)

# بخش ۳: نحوه دریافت مبلغ
st.header("۳. نحوه دریافت مبلغ")
payment_method = st.selectbox("نوع دریافت مبلغ:", [
    "دریافت نقد", "دریافت به حساب بانک", "کارت به کارت به مشتری", "دریافت طلا", "دریافت ارز"
])

payment_details = ""
gold_weight = 0.0
gold_price = 0.0

if payment_method == "دریافت به حساب بانک":
    selected_bank = st.selectbox("حساب بانکی مقصد:", BANKS)
    payment_details = f"واریز به {selected_bank}"
elif payment_method == "کارت به کارت به مشتری":
    card_number = st.text_input("شماره کارت مشتری:")
    payment_details = f"کارت به کارت از مشتری به شماره: {card_number}"
elif payment_method == "دریافت طلا":
    st.warning("جزئیات طلای دریافتی را وارد کنید")
    gold_weight = st.number_input("وزن طلای دریافتی (گرم)", min_value=0.0, format="%.2f")
    gold_price = st.number_input("قیمت هر گرم طلا (تومان)", min_value=0)
    payment_details = f"دریافت {gold_weight} گرم طلا به قیمت هر گرم {gold_price} تومان"
elif payment_method == "دریافت ارز":
    currency_type = st.selectbox("نوع ارز:", ["دلار", "یورو", "درهم", "پوند"])
    currency_amount = st.number_input("مقدار ارز دریافتی", min_value=0.0, format="%.2f")
    payment_details = f"دریافت {currency_amount} {currency_type}"

# بخش ۴: آپلود عکس
st.header("۴. مدارک و عکس‌ها")
uploaded_files = st.file_uploader("عکس‌های محصول یا فیش واریزی را انتخاب کنید", 
                                 accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

# بخش ۵: ذخیره نهایی
st.header("۵. ثبت نهایی")
if st.button("ثبت و ذخیره فاکتور", type="primary"):
    if not item_type or final_price == 0:
        st.error("لطفاً نوع جنس و مبلغ نهایی را وارد کنید.")
    else:
        record = {
            "شماره فاکتور": invoice_id,
            "تاریخ و زمان": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ثبت کننده": user,
            "نوع جنس": item_type,
            "توضیحات": item_desc,
            "وزن (گرم)": weight,
            "وضعیت": condition,
            "اجرت (تومان)": making_charge,
            "مبلغ نهایی (تومان)": final_price,
            "روش دریافت": payment_method,
            "جزئیات دریافت": payment_details,
            "وزن طلا دریافتی": gold_weight,
            "قیمت طلا": gold_price,
            "تعداد عکس": len(uploaded_files) if uploaded_files else 0
        }
        
        # ذخیره در فایل CSV
        df = pd.DataFrame([record])
        if os.path.exists(CSV_FILE):
            df.to_csv(CSV_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(CSV_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')
            
        # ذخیره عکس‌ها
        if uploaded_files:
            for img in uploaded_files:
                img_path = os.path.join("images", f"{invoice_id}_{img.name}")
                with open(img_path, "wb") as f:
                    f.write(img.getbuffer())
        
        st.success(f"فاکتور با شماره {invoice_id} با موفقیت ثبت شد!")
        st.balloons()

# نمایش رکوردها
st.divider()
st.header("📋 گزارشات ثبت شده")
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    st.dataframe(df, use_container_width=True)
else:
    st.info("هنوز فاکتوری ثبت نشده است.")