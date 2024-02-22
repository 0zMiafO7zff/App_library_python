from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import errorcode

win = Tk()
win.geometry('900x520')
win.option_add('*font', 'tahoma 10')
win.option_add('*Button*background', 'lightgray')

cnx = mysql.connector.connect(user="root", password="", host="127.0.0.1", database="db_library")
cusor = cnx.cursor()

show_columns = ['id', 'm_user', 'm_pass', 'm_name', 'm_phone']
column_widths = [4, 15, 15, 15, 10, 13]

def show_data():
    for row in tree.get_children():
        tree.delete(row)
    
    sql = 'SELECT * FROM tb_members'
    cusor.execute(sql)
    rows = cusor.fetchall()

    for row in rows:
        tree.insert('', 'end', values=row)

tree = ttk.Treeview(win, columns=show_columns, show='headings', height=15)
for col, heading in zip(show_columns, ['ลำดับ', 'ชื่อผู้ใช้', 'รหัสผ่าน', 'ชื่อ-สกุล', 'เบอร์โทร']):
    tree.heading(col, text=heading)
    tree.column(col, width=100)
tree.grid(row=0, column=0, padx=10, pady=10)

show_data()

frame = LabelFrame(win, text='เพิ่มหรือแก้ไขข้อมูล')
frame.grid(row=0, column=1, padx=10, pady=5)

def add_grid(w, r, c, cspan=1):
    w.grid(row=r, column=c, columnspan=cspan, sticky=W, padx=10, pady=5)

add_grid(Label(frame, text='ค้นหาสมาชิก:'), r=0, c=0)
ent_ID = Entry(frame, width=20)
add_grid(ent_ID, r=0, c=1, cspan=2)

add_grid(Label(frame, text='รหัสผู้ใช้งาน:'), r=1, c=0)
ent_UserID = Entry(frame, width=20)
add_grid(ent_UserID, r=1, c=1, cspan=2)

add_grid(Label(frame, text='รหัสผ่าน:'), r=2, c=0)
ent_pass = Entry(frame, width=20)
add_grid(ent_pass, r=2, c=1, cspan=2)

add_grid(Label(frame, text='ชื่อผู้ใช้งาน:'), r=3, c=0)
ent_name = Entry(frame, width=20)
add_grid(ent_name, r=3, c=1, cspan=2)

add_grid(Label(frame, text='เบอร์โทรศัพท์:'), r=4, c=0)
ent_phone = Entry(frame, width=20)
add_grid(ent_phone, r=4, c=1, cspan=2)

bt_add = Button(frame, text='เพิ่ม', command=lambda: add_data())
bt_add.grid(row=5, column=2, padx=10, pady=10)

bt_update = Button(frame, text='แก้ไข', command=lambda: update_data())
bt_update.grid(row=5, column=3, padx=10, pady=10)



bt_search = Button(frame, text='ค้นหา', command=lambda: search())
bt_search.grid(row=5, column=1, padx=10, pady=10)

entries = [ent_ID, ent_UserID, ent_pass, ent_name, ent_phone]

frame_del = LabelFrame(win, text='ลบข้อมูล')
frame_del.grid(row=1, column=1, padx=10, pady=5, sticky=W+E)
Label(frame_del, text='รหัสพนักงาน:').pack(side=LEFT, padx=10, pady=10)
ent_id_del = Entry(frame_del, width=10)
ent_id_del.pack(side=LEFT, padx=10, pady=10)
bt_del = Button(frame_del, text='ลบ', command=lambda: delete_data())
bt_del.pack(side=LEFT, padx=10, pady=10)

def search():
    kw = ent_ID.get()
    sql = f"SELECT * FROM tb_members WHERE id = '{kw}' OR m_user LIKE '%{kw}%' OR m_name LIKE '%{kw}%'"
    cusor.execute(sql)
    rows = cusor.fetchall()

    if rows:
        for row in rows:
            set_text_entry(ent_ID, row[0])
            set_text_entry(ent_UserID, row[1])
            set_text_entry(ent_pass, row[2])
            set_text_entry(ent_name, row[3])
            set_text_entry(ent_phone, row[4])
        messagebox.showinfo('Success', 'ค้นหาเสร็จสิ้น')
    else:
        messagebox.showerror('Error', 'ไม่พบข้อมูล')


def set_text_entry(ent, text):
    ent.delete(0, END)
    ent.insert(0, text)

def get_data():
    return [ent.get() for ent in entries]

def add_data():
    data = get_data()
    
    # ตรวจสอบว่าข้อมูลที่ป้อนครบหรือไม่ ยกเว้น m_user และ m_pass
    if data[1] == '' or data[2] == '':
        messagebox.showerror('Error', 'กรุณากรอกข้อมูลให้ครบ')
        return
    
    # ตรวจสอบความยาวของเบอร์โทร
    if data[4]:
        try:
            int(data[4])  # พยายามแปลงข้อมูลเป็น int
        except ValueError:
            messagebox.showerror('Error', 'กรุณากรอกเป็นตัวเลขเท่านั้น')
            return
            
        if len(data[4]) != 10:
            messagebox.showerror('Error', 'กรุณากรอกเบอร์โทรให้ครบ 10 ตัว')
            return
    
    # ตรวจสอบชนิดข้อมูลของข้อมูลที่กรอกเข้ามา
    data_types = [type(d) for d in data[1:]]
    expected_data_types = [str, str, str, str]  # ระบุชนิดข้อมูลที่ต้องการสำหรับแต่ละช่อง
    
    if data_types != expected_data_types:
        messagebox.showerror('Error', 'กรุณากรอกชนิดข้อมูลให้ตรง')
        return
    
    sql = 'INSERT INTO tb_members (m_user, m_pass, m_name, m_phone) VALUES (%s, %s, %s, %s)'
    try:
        cusor.execute(sql, data[1:])
        cnx.commit()
        messagebox.showinfo('Success', 'ข้อมูลถูกบันทึกแล้ว')
        show_data()
        clear_data()
    except Exception as e:
        print(e)
        messagebox.showerror('Error', 'เกิดข้อผิดพลาด ข้อมูลไม่ถูกบันทึก')




def update_data():
    data = get_data()
    sql = 'UPDATE tb_members SET m_user = %s, m_pass = %s, m_name = %s, m_phone = %s WHERE id = %s'
    try:
        cusor.execute(sql, data[1:] + [data[0]])
        cnx.commit()
        messagebox.showinfo('Success', 'ทำรายการสำเร็จ')
        show_data()
        clear_data()
    except Exception as e:
        print(e)
        messagebox.showerror('Error', 'เกิดข้อผิดพลาด ข้อมูลไม่ถูกอัปเดต')
from tkinter import messagebox


    

def delete_data():
    # ให้ดึง id จาก entry widget ของคุณ สมมติว่ามีตัวแปรชื่อว่า ent_id_del
    id = ent_id_del.get()
    confirm_delete = messagebox.askyesno("ยืนยันการลบข้อมูล", "คุณแน่ใจหรือไม่ที่จะลบข้อมูลสมาชิก?")
    if confirm_delete:
        sql_check_id = 'SELECT * FROM tb_members WHERE id = %s'
        cusor.execute(sql_check_id, (id,))
        existing_id = cusor.fetchone()
        if not existing_id:
            messagebox.showerror('Error', 'ไม่พบ ID นี้ในฐานข้อมูล')
            return
        
        sql = 'DELETE FROM tb_members WHERE id = %s'
        try:
            cusor.execute(sql, [id])
            cnx.commit()
            messagebox.showinfo('Success', 'ข้อมูลถูกลบแล้ว')
            show_data()
            ent_id_del.delete(0, 'end')
        except Exception as e:
            print(e)
            messagebox.showerror('Error', 'เกิดข้อผิดพลาด ข้อมูลไม่ถูกลบ')



def clear_data():
    for ent in entries:
        ent.delete(0, END)

mainloop()
