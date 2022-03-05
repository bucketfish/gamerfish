list = "["

numbers = ['A', '2', '3', '4']
suits = ['♦', '♣', '♥', '♠']

for i in range(0, 4):
    for j in range(0, 4):
        list += '"' + numbers[i] + suits[j] + '",'

print (list)
