data = {}

with open('材料.txt',encoding='utf-8') as f:
   for line in f:
       line = line.strip()
       parts = line.split('，')
       data[parts[0]] = parts[1:]

while True:
    name = input('你想查什么材料?(输入q退出)')

    if name =='q':
        break
    
    if name in data:
        print('，'.join(data[name]))
    else:
        print('没有该材料')