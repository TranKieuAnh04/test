import tkinter as tk
from tkinter import messagebox
import random
import matplotlib.pyplot as plt
#import networkx as nx
def generate_random_data():
    num_transactions = int(entry_num_rows.get())
    items = entry_custom_items.get().split(',') if entry_custom_items.get() else ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    transactions.clear()
    for _ in range(num_transactions):
        random_items = sorted(random.sample(items, random.randint(2, min(4, len(items)))))
        transactions.append(random_items)
    display_transactions()

def load_default_data():
    global transactions
    transactions = [['A', 'C', 'D'],
                    ['B', 'C', 'E'],
                    ['A', 'B', 'C', 'E'],
                    ['B', 'E']]
    display_transactions()

def display_transactions():
    text_data.delete("1.0", tk.END)
    for items in transactions:
        text_data.insert(tk.END, f"{','.join(sorted(items))}\n")

def update_transactions_from_textbox():
    global transactions
    transactions = []
    data = text_data.get("1.0", tk.END).strip()
    if data:
        transactions = [line.split(',') for line in data.split("\n") if line]

def reset_data():
    transactions.clear()
    text_data.delete("1.0", tk.END)
    text_result.delete("1.0", tk.END)
    text_steps.delete("1.0", tk.END)

def count_support(itemset):
    return sum(1 for t in transactions if itemset.issubset(t))

def has_infrequent_subset(candidate, Lk):
    """ Kiểm tra nếu tập con của tập ứng viên không thuộc tập phổ biến """
    subsets = [frozenset(candidate - {item}) for item in candidate]
    return any(subset not in Lk for subset in subsets)

def apriori_gen(Lk):
    """ Sinh tập ứng viên (Ck+1) từ tập phổ biến (Lk) """
    Ck_plus_1 = set()
    Lk_list = list(Lk.keys())

    for i in range(len(Lk_list)):
        for j in range(i + 1, len(Lk_list)):
            l1, l2 = Lk_list[i], Lk_list[j]
            candidate = l1 | l2  # Hợp hai tập phổ biến
            if len(candidate) == len(l1) + 1:  # Chỉ chấp nhận tập có đúng k+1 phần tử
                if not has_infrequent_subset(candidate, Lk):
                    Ck_plus_1.add(candidate)

    return {itemset: 0 for itemset in Ck_plus_1}

def apriori_algorithm():
    global steps, step_index
    update_transactions_from_textbox()
    if not transactions:
        messagebox.showerror("Lỗi", "Vui lòng nhập hoặc tạo dữ liệu trước!")
        return
    
    try:
        min_support = float(entry_minsup.get()) / 100
    except ValueError:
        messagebox.showerror("Lỗi", "Giá trị minsup không hợp lệ!")
        return
    
    min_count = min_support * len(transactions)
    
    # Bước 1: Khởi tạo C1 và L1
    item_counts = {}
    for transaction in transactions:
        for item in transaction:
            item_counts[item] = item_counts.get(item, 0) + 1
    
    C1 = {frozenset([item]): count for item, count in item_counts.items()}
    L1 = {itemset: count for itemset, count in C1.items() if count >= min_count}
    
    steps = ["Các tập phổ biến L1:"]
    for item, count in C1.items():
        support_percent = (count / len(transactions)) * 100
        if count >= min_count:
            steps.append(f"{set(item)} (support = {count} ({support_percent:.0f}%))")
        else:
            steps.append(f"{set(item)} (support = {count} ({support_percent:.0f}%)) \u2192 Loại (\u2264 minsup)")
    
    all_frequent_itemsets = set(L1.keys())
    Lk = L1
    k = 2
    
    while Lk:
        Ck_plus_1 = apriori_gen(Lk)
        
        for transaction in transactions:
            for candidate in Ck_plus_1:
                if candidate.issubset(transaction):
                    Ck_plus_1[candidate] += 1
        
        Lk_plus_1 = {itemset: count for itemset, count in Ck_plus_1.items() if count >= min_count}
        
        if Lk_plus_1:
            steps.append(f"\nCác tập phổ biến L{k}:")
            for item, count in Ck_plus_1.items():
                support_percent = (count / len(transactions)) * 100
                if count >= min_count:
                    steps.append(f"{set(item)} (support = {count} ({support_percent:.0f}%))")
                else:
                    steps.append(f"{set(item)} (support = {count} ({support_percent:.0f}%)) \u2192 Loại (\u2264 minsup)")
        
        if not Lk_plus_1:
            steps.append("\nKhông thể xây dựng tập ứng viên nào nữa. Dừng thuật toán.")
            break
        
        all_frequent_itemsets.update(Lk_plus_1.keys())
        Lk = Lk_plus_1
        k += 1
    
    text_result.delete("1.0", tk.END)
    text_result.insert(tk.END, "Tập phổ biến:\n", "bold")
    sorted_itemsets = sorted(all_frequent_itemsets, key=lambda x: (len(x), sorted(x)))
    
    for idx, itemset in enumerate(sorted_itemsets, 1):
        support_count = count_support(itemset)
        support_ratio = (support_count / len(transactions)) * 100
        text_result.insert(tk.END, f"{idx}. {set(itemset)} supp = {support_count} ({support_ratio:.0f}%)\n")
    text_result.insert(tk.END, "\nCác tập phổ biến: \n", "bold")
    text_result.insert(tk.END, f"{[set(itemset) for itemset in sorted_itemsets]}\n")
    
    step_index = 0  # Reset bước hiển thị
    text_steps.delete("1.0", tk.END)
    
def show_next_step():
    global step_index
    if step_index < len(steps):
        # Nếu bước hiện tại là tiêu đề của Lx, hiển thị tiêu đề trước với chữ in đậm
        if steps[step_index].startswith("\nCác tập phổ biến L"):
            text_steps.insert(tk.END, steps[step_index] + "\n", "bold")
            step_index += 1

        # Hiển thị toàn bộ danh sách của Lx cho đến khi gặp tiêu đề mới
        while step_index < len(steps) and not steps[step_index].startswith("\nCác tập phổ biến L"):
            text_steps.insert(tk.END, steps[step_index] + "\n")
            step_index += 1
    else:
        messagebox.showinfo("Thông báo", "Đã hiển thị hết các bước!")



# def draw_apriori_graph(Ck_list, Lk_list):
#     fig, ax = plt.subplots(figsize=(10, 6))
#     G = nx.DiGraph()
#     pos = {}
    
#     y_offset = 0  # Điều chỉnh độ cao của từng bước
#     previous_nodes = []
    
#     for k, (Ck, Lk) in enumerate(zip(Ck_list, Lk_list), start=1):
#         current_nodes = []
#         for idx, itemset in enumerate(Ck):
#             node_label = f"{set(itemset)}\nC{k}"
#             G.add_node(node_label, level=k)
#             pos[node_label] = (idx, -y_offset)
#             current_nodes.append(node_label)
            
#             if itemset in Lk:
#                 G.nodes[node_label]['color'] = 'lightgreen'
#             else:
#                 G.nodes[node_label]['color'] = 'lightcoral'
        
#         if previous_nodes:
#             for prev_node in previous_nodes:
#                 for curr_node in current_nodes:
#                     G.add_edge(prev_node, curr_node)
        
#         previous_nodes = current_nodes
#         y_offset += 2  # Tăng khoảng cách giữa các bước
    
#     colors = [G.nodes[n].get('color', 'skyblue') for n in G.nodes]
#     nx.draw(G, pos, with_labels=True, node_size=3000, node_color=colors, edge_color='gray', font_size=10, font_weight='bold', ax=ax)
#     plt.title("Quá trình sinh tập ứng viên và tập phổ biến")
#     plt.show()

# # Hàm gọi vẽ biểu đồ sau khi chạy thuật toán Apriori
# def plot_apriori_result():
#     if not transactions:
#         messagebox.showerror("Lỗi", "Chưa có dữ liệu giao dịch!")
#         return
    
#     update_transactions_from_textbox()
#     try:
#         min_support = float(entry_minsup.get()) / 100
#     except ValueError:
#         messagebox.showerror("Lỗi", "MinSup không hợp lệ!")
#         return
    
#     min_count = min_support * len(transactions)
#     Ck_list, Lk_list = [], []
    
#     item_counts = {}
#     for transaction in transactions:
#         for item in transaction:
#             item_counts[item] = item_counts.get(item, 0) + 1
    
#     C1 = {frozenset([item]): count for item, count in item_counts.items()}
#     L1 = {itemset: count for itemset, count in C1.items() if count >= min_count}
    
#     Ck_list.append(C1.keys())
#     Lk_list.append(L1.keys())
    
#     Lk = L1
#     while Lk:
#         Ck_plus_1 = apriori_gen(Lk)
#         for transaction in transactions:
#             for candidate in Ck_plus_1:
#                 if candidate.issubset(transaction):
#                     Ck_plus_1[candidate] += 1
        
#         Lk_plus_1 = {itemset: count for itemset, count in Ck_plus_1.items() if count >= min_count}
        
#         Ck_list.append(Ck_plus_1.keys())
#         Lk_list.append(Lk_plus_1.keys())
        
#         if not Lk_plus_1:
#             break
#         Lk = Lk_plus_1
    
#     draw_apriori_graph(Ck_list, Lk_list)

root = tk.Tk()
root.title("Thuật toán Apriori")
root.state("zoomed")
transactions = []
steps = []
step_index = 0

frame_controls = tk.Frame(root)
frame_controls.pack(pady=10)

tk.Label(frame_controls, text="Số giao dịch:", font=("Times New Roman", 14)).grid(row=0, column=0)
entry_num_rows = tk.Entry(frame_controls, width=5, font=("Times New Roman", 14))
entry_num_rows.grid(row=0, column=1, padx=10, pady=5)
entry_num_rows.insert(0, "4")

tk.Label(frame_controls, text="MinSupp (%):", font=("Times New Roman", 14)).grid(row=0, column=5)
entry_minsup = tk.Entry(frame_controls, width=5, font=("Times New Roman", 14))
entry_minsup.grid(row=0, column=6)
entry_minsup.insert(0, "50")

tk.Label(frame_controls, text="Tập mục tùy chỉnh:", font=("Times New Roman", 14)).grid(row=1, column=0)
entry_custom_items = tk.Entry(frame_controls, width=30, font=("Times New Roman", 14))
entry_custom_items.grid(row=1, column=1, columnspan=5, padx=10, pady=10)

btn_generate = tk.Button(frame_controls, text="Random", command=generate_random_data, font=("Arial", 13), bg='#2196F3', fg='white')
btn_generate.grid(row=2, column=0, padx=5, pady=5)


btn_load_default = tk.Button(frame_controls, text="Dữ liệu gốc", command=load_default_data,font=("Arial", 13), bg='#2196F3', fg='white')
btn_load_default.grid(row=2, column=1, padx=5)

btn_solve = tk.Button(frame_controls, text="Bắt đầu giải", command=apriori_algorithm,font=("Arial", 13), bg='#4CAF50', fg='white')
btn_solve.grid(row=2, column=3, padx=5)

btn_next_step = tk.Button(frame_controls, text="Từng bước giải", command=show_next_step,font=("Arial", 13),bg='#FF9800', fg='white')
btn_next_step.grid(row=2, column=5, padx=5)

btn_reset = tk.Button(frame_controls, text="Reset", command=reset_data,font=("Arial", 13))
btn_reset.grid(row=2, column=6, padx=5)

frame_data = tk.Frame(root)
frame_data.pack()

tk.Label(frame_data, text="Dữ liệu giao dịch:", font=("Times New Roman", 14, "bold")).pack()
text_data = tk.Text(frame_data, height=8, width=40, font=("Times New Roman", 14))
text_data.pack()

frame_main = tk.Frame(root)
frame_main.pack(fill=tk.BOTH, expand=True)

# Khung "Kết quả" (bên trái)
frame_result = tk.Frame(frame_main)
frame_result.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)

tk.Label(frame_result, text="Kết quả:", font=("Times New Roman", 14, "bold")).pack()
text_result = tk.Text(frame_result, height=15, width=40, font=("Times New Roman", 13))
text_result.tag_configure("bold", font=("Times New Roman", 13, "bold"))  # Thiết lập in đậm

text_result.pack(fill=tk.BOTH, expand=True)

# Khung "Từng bước giải" (bên phải)
frame_steps = tk.Frame(frame_main)
frame_steps.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=30)  # padx=10 tạo khoảng cách 1cm

tk.Label(frame_steps, text="Từng bước giải:", font=("Times New Roman", 14, "bold")).pack()
text_steps = tk.Text(frame_steps, height=15, width=40, font=("Times New Roman", 13))
text_steps.tag_configure("bold", font=("Times New Roman", 13, "bold"))

text_steps.pack(fill=tk.BOTH, expand=True)


# btn_plot = tk.Button(frame_controls, text="Vẽ biểu đồ", command=plot_apriori_result, font=("Arial", 13), bg='#673AB7', fg='white')
# btn_plot.grid(row=2, column=7, padx=5)




root.mainloop()
