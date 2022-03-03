list = "["

numbers = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
suits = ['♦', '♣', '♥', '♠']

for i in range(0, 13):
    for j in range(0, 4):
        list += '"' + numbers[i] + suits[j] + '",'

print (list)
