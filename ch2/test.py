
import codecs

def loadRatings(path=''):
    #dataPool
    data = {}

    f = codecs.open(path + 'kitchen-ratings.csv','r','utf8');


    for line in f:
        fields = line.split(',')
        uid = fields[0].strip('"')
        kit_id = fields[1].strip('"')
        rating = int(fields[2].strip().strip('"'))
        if uid in data:
            currentRatings = data[uid]
        else:
            currentRatings = {}

        currentRatings[kit_id] = rating
        data[uid] = currentRatings

    f.close()
    print(data)


#product
def loadProduct(path=''):
    #dataPool
    data = {}

    f = codecs.open(path + 'kitchen.csv','r','utf8');

    productid2name = {}

    for line in f:
        fields = line.split(',')
        kit_id = fields[0].strip('"')
        kit_name = fields[1].strip('"')
        productid2name[kit_id] = kit_name

    f.close()
    print(productid2name)


def loadUsers(path=''):
    #dataPool
    userid2name = {}

    f = codecs.open(path + 'users.csv','r','utf8');


    for line in f:
        fields = line.split(',')
        uid = fields[0].strip('"')
        nickname = fields[1].strip('"')
        userid2name[uid] = nickname

    f.close()
    print(userid2name)

if __name__ == '__main__':
    loadRatings("./")#Ratings
    loadProduct("./")#kitchen
    loadUsers("./")  # users