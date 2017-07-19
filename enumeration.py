
l1 = ['NS1', 'ES1', 'EA1']
l2 = ['AS2', 'NS1']
l3 = ['AA2', 'AS2']

for i in l1:
    for j in l2:
        for k in l3:
            print('{} {} {}'.format(i, j, k))