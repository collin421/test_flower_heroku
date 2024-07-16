from flask import Blueprint, render_template, request, send_file
from .func import get_db
import datetime
import pandas as pd
from io import BytesIO


dashboard_blueprint = Blueprint('dashboard', __name__, template_folder='templates')

@dashboard_blueprint.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    db = get_db()  # 데이터베이스 연결 가져오기
    current_year = datetime.datetime.now().year
    selected_year = int(request.form.get('year', current_year))
    
    # 모든 지점 및 날짜 리스트 가져오기
    cur = db.cursor()
    cur.execute('SELECT DISTINCT name FROM branches')
    branches = [row['name'] for row in cur.fetchall()]
    
    start_date = datetime.date(selected_year, 1, 1)
    end_date = datetime.date(selected_year, 12, 31)
    dates = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    
    # 매출 데이터를 쿼리하여 가져오기
    cur.execute('''
        SELECT s.sale_date, b.name AS branch_name, 
               s.sales_card_sweetdream, s.sales_card_glory, 
               s.sales_cash, s.sales_zeropay, 
               s.sales_transfer, s.total_sales
        FROM sales s
        JOIN branches b ON s.branch_id = b.id
        WHERE strftime('%Y', s.sale_date) = ?
        ORDER BY s.sale_date, b.name
    ''', (str(selected_year),))
    
    sales_data = cur.fetchall()
    cur.close()
    
    # 데이터를 지점별로 그룹화하고 일별 매출 합계 계산
    sales_by_branch = {branch: {date: {'sales_card_sweetdream': 0, 'sales_card_glory': 0, 'sales_cash': 0, 'sales_zeropay': 0, 'sales_transfer': 0, 'total_sales': 0} for date in dates} for branch in branches}
    total_sales_by_date = {date: 0 for date in dates}
    
    for row in sales_data:
        date = datetime.datetime.strptime(row['sale_date'], '%Y-%m-%d').date()
        branch = row['branch_name']
        sales_by_branch[branch][date]['sales_card_sweetdream'] += row['sales_card_sweetdream']
        sales_by_branch[branch][date]['sales_card_glory'] += row['sales_card_glory']
        sales_by_branch[branch][date]['sales_cash'] += row['sales_cash']
        sales_by_branch[branch][date]['sales_zeropay'] += row['sales_zeropay']
        sales_by_branch[branch][date]['sales_transfer'] += row['sales_transfer']
        sales_by_branch[branch][date]['total_sales'] += row['total_sales']
        total_sales_by_date[date] += row['total_sales']
    
    return render_template('dashboard.html', 
                           sales_by_branch=sales_by_branch, 
                           dates=dates, 
                           branches=branches, 
                           selected_year=selected_year, 
                           current_year=current_year, 
                           total_sales_by_date=total_sales_by_date,
                           today=datetime.date.today())



@dashboard_blueprint.route('/download-sales-excel')
def download_sales_excel():
    try:
        db = get_db()
        cur = db.cursor()
        selected_year = datetime.datetime.now().year  # 현재 연도를 기본값으로 사용
        start_date = datetime.date(selected_year, 1, 1)
        end_date = datetime.date(selected_year, 12, 31)
        date_range = pd.date_range(start=start_date, end=end_date)

        # 데이터베이스 쿼리 실행
        cur.execute('''
            SELECT s.sale_date, b.name AS branch_name, s.sales_card_sweetdream, s.sales_card_glory, 
                   s.sales_cash, s.sales_zeropay, s.sales_transfer, s.total_sales
            FROM sales s
            JOIN branches b ON s.branch_id = b.id
            WHERE strftime('%Y', s.sale_date) = ?
            ORDER BY s.sale_date, b.name
        ''', (str(selected_year),))
        sales_data = cur.fetchall()
        cur.close()

        # 데이터프레임 생성
        sales_df = pd.DataFrame(sales_data, columns=['Sale Date', 'Branch Name', 'Card SweetDream', 'Card Glory', 'Cash', 'ZeroPay', 'Transfer', 'Total Sales'])
        sales_df['Sale Date'] = pd.to_datetime(sales_df['Sale Date'])

        # 모든 날짜에 대한 데이터프레임 생성
        all_dates_df = pd.DataFrame(date_range, columns=['Sale Date'])

        # 병합을 위한 'Sale Date' 열을 datetime 형식으로 변환
        merged_df = pd.merge(all_dates_df, sales_df, on='Sale Date', how='left').fillna(0)

        # 디버깅: 데이터프레임 내용 출력
        print(merged_df.head())

        # 엑셀 파일로 변환
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            merged_df.to_excel(writer, index=False, sheet_name='Sales Data')
        output.seek(0)

        return send_file(output, download_name=f"sales_data_{selected_year}.xlsx", as_attachment=True)
    
    except Exception as e:
        # 로깅 또는 디버깅을 위해 오류 메시지를 출력합니다.
        print(f"Error: {e}")
        return "엑셀 파일을 생성하는 동안 오류가 발생했습니다.", 500

