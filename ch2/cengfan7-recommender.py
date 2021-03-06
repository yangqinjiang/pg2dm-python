import codecs
import MySQLdb
from math import sqrt

users = {"Angelica": {"Blues Traveler": 3.5, "Broken Bells": 2.0,
                      "Norah Jones": 4.5, "Phoenix": 5.0,
                      "Slightly Stoopid": 1.5,
                      "The Strokes": 2.5, "Vampire Weekend": 2.0},

         "Bill": {"Blues Traveler": 2.0, "Broken Bells": 3.5,
                  "Deadmau5": 4.0, "Phoenix": 2.0,
                  "Slightly Stoopid": 3.5, "Vampire Weekend": 3.0},

         "Chan": {"Blues Traveler": 5.0, "Broken Bells": 1.0,
                  "Deadmau5": 1.0, "Norah Jones": 3.0, "Phoenix": 5,
                  "Slightly Stoopid": 1.0},

         "Dan": {"Blues Traveler": 3.0, "Broken Bells": 4.0,
                 "Deadmau5": 4.5, "Phoenix": 3.0,
                 "Slightly Stoopid": 4.5, "The Strokes": 4.0,
                 "Vampire Weekend": 2.0},

         "Hailey": {"Broken Bells": 4.0, "Deadmau5": 1.0,
                    "Norah Jones": 4.0, "The Strokes": 4.0,
                    "Vampire Weekend": 1.0},

         "Jordyn": {"Broken Bells": 4.5, "Deadmau5": 4.0,
                    "Norah Jones": 5.0, "Phoenix": 5.0,
                    "Slightly Stoopid": 4.5, "The Strokes": 4.0,
                    "Vampire Weekend": 4.0},

         "Sam": {"Blues Traveler": 5.0, "Broken Bells": 2.0,
                 "Norah Jones": 3.0, "Phoenix": 5.0,
                 "Slightly Stoopid": 4.0, "The Strokes": 5.0},

         "Veronica": {"Blues Traveler": 3.0, "Norah Jones": 5.0,
                      "Phoenix": 4.0, "Slightly Stoopid": 2.5,
                      "The Strokes": 3.0}
         }


class recommender:
    def __init__(self, data, k=1, metric='pearson', n=5):
        """ initialize recommender
        currently, if data is dictionary the recommender is initialized
        to it.
        For all other data types of data, no initialization occurs
        k is the k value for k nearest neighbor
        metric is which distance formula to use
        n is the maximum number of recommendations to make"""
        self.k = k
        self.n = n
        self.username2id = {}
        self.userid2name = {}
        self.productid2name = {}
        # for some reason I want to save the name of the metric
        self.metric = metric
        if self.metric == 'pearson':
            self.fn = self.pearson
        #
        # if data is dictionary set recommender data to it
        #
        if type(data).__name__ == 'dict':
            self.data = data

    def convertProductID2name(self, id):
        """Given product id number return product name"""
        if id in self.productid2name:
            return self.productid2name[id]
        else:
            return id

    def userRatings(self, id, n):
        """Return n top ratings for user with id"""
        print ("Ratings for " + self.userid2name[id])
        ratings = self.data[id]
        print(len(ratings))
        ratings = list(ratings.items())
        ratings = [(self.convertProductID2name(k), v)
                   for (k, v) in ratings]
        # finally sort and return
        ratings.sort(key=lambda artistTuple: artistTuple[1],
                     reverse=True)
        ratings = ratings[:n]
        for rating in ratings:
            print("%s\t%i" % (rating[0], rating[1]))

    def loadBookDB(self, path=''):
        """loads the BX book dataset. Path is where the BX files are
        located"""
        self.data = {}
        i = 0
        #
        # First load book ratings into self.data
        #
        f = codecs.open(path + "kitchen-ratings.csv", 'r', 'utf8')
        for line in f:
            i += 1
            # separate line into fields
            fields = line.split(',')
            uid = fields[0].strip('"')
            kit_id = fields[1].strip('"')
            rating = int(fields[2].strip().strip('"'))
            if uid in self.data:
                currentRatings = self.data[uid]
            else:
                currentRatings = {}

            currentRatings[kit_id] = rating
            self.data[uid] = currentRatings
        f.close()
        #
        # Now load books into self.productid2name
        # Books contains isbn, title, and author among other fields
        #
        f = codecs.open(path + "kitchen.csv", 'r', 'utf8')
        for line in f:
            i += 1
            # separate line into fields
            fields = line.split(',')
            kit_id = fields[0].strip('"')
            kit_name = fields[1].strip('"')
            self.productid2name[kit_id] = kit_name
        f.close()


        #
        #  Now load user info into both self.userid2name and
        #  self.username2id
        #
        f = codecs.open(path + "users.csv", 'r', 'utf8')
        for line in f:
            i += 1
            # print(line)
            # separate line into fields
            fields = line.split(',')
            uid = fields[0].strip('"')
            nickname = fields[1].strip('"')
            self.userid2name[uid] = nickname
        f.close()
        print(i)


    def loadBookDB2(self, db_name,host='',user='',passwd='',port=3306,charset='utf8'):
        """loads the BX book dataset. Path is where the BX files are
        located"""
        self.data = {}



        print 'fetch rating ......'
        #
        # ratings
        #
        try:
            conn = MySQLdb.connect(host=host, user=user, passwd=passwd, port=port, charset=charset)
            cur = conn.cursor()
            conn.select_db(db_name)
            #kitchen-ratings
            count = cur.execute("SELECT diners_id,kit_id,ROUND(AVG(score),1) from c_comment WHERE order_id != 0  GROUP BY diners_id,kit_id ;");
            print 'there has %s rows record '%count
            results = cur.fetchall()
            for r in results:
                # print 'uid=%s kit_id=%s  score=%s'%(r)
                uid = r[0]
                kit_id= r[1]
                rating = r[2]
                if uid in self.data:
                    currentRatings = self.data[uid]
                else:
                    currentRatings = {}

                currentRatings[kit_id] = float(rating)
                self.data[uid] = currentRatings

            # print self.data
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])



        print 'fetch kitchen ......'
        # kitchen
        self.productid2name = {}
        try:
            conn = MySQLdb.connect(host=host, user=user, passwd=passwd, port=port, charset=charset)
            cur = conn.cursor()
            conn.select_db(db_name)
            # kitchen
            count = cur.execute("SELECT id ,name FROM c_kitchen WHERE onshelf = 1;")
            print 'there has %s rows record ' % count
            kit_results = cur.fetchall()
            for r in kit_results:
                # print 'kit_id=%s  kit_name=%s'%(r)

                kit_id = r[0]
                kit_name = r[1]
                self.productid2name[kit_id] = kit_name

            # print self.productid2name
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])


        #users
        print 'fetch users ......'
        # users
        try:
            conn = MySQLdb.connect(host=host, user=user, passwd=passwd, port=port, charset=charset)
            cur = conn.cursor()
            conn.select_db(db_name)
            # kitchen
            count = cur.execute("SELECT d.id,d.nickname from c_orders as o INNER JOIN c_diners as d ON o.diners_id = d.id WHERE o.payment_status =1 GROUP BY d.id;")
            print 'there has %s rows record ' % count
            kit_results = cur.fetchall()
            for r in kit_results:
                # print 'uid=%s  kit_name=%s'%(r)

                uid = r[0]
                nickname = r[1]
                self.userid2name[uid] = nickname


            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])


    def pearson(self, rating1, rating2):
        # print 'rating1=%s'%rating1
        # print 'rating2=%s'%rating2
        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_y2 = 0
        n = 0
        for key in rating1:
            if key in rating2:
                n += 1
                x = rating1[key]
                y = rating2[key]
                # print 'x=%s,y=%s'%(x,y)
                sum_xy += x * y
                sum_x += x
                sum_y += y
                sum_x2 += pow(x, 2)
                sum_y2 += pow(y, 2)
        if n == 0:
            return 0
        # now compute denominator
        denominator = (sqrt(sum_x2 - pow(sum_x, 2) / n)
                       * sqrt(sum_y2 - pow(sum_y, 2) / n))

        # print  'denominator=%s'%denominator

        if denominator == 0:
            return 0
        else:
            return (sum_xy - (sum_x * sum_y) / n) / denominator

    def computeNearestNeighbor(self, username):
        """creates a sorted list of users based on their distance to
        username"""

        distances = []
        # print self.data
        for instance in self.data:
            if instance != username and username in self.data:
                # print 'username=%s ,instance=%s'%(username,instance)
                distance = self.fn(self.data[username],
                                   self.data[instance])
                distances.append((instance, distance))
        # sort based on distance -- closest first
        distances.sort(key=lambda artistTuple: artistTuple[1],
                       reverse=True)

        return distances

    def recommend(self, user):
        """Give list of recommendations"""
        recommendations = {}

        if user not in self.data:
            return  recommendations
        # first get list of users  ordered by nearness
        nearest = self.computeNearestNeighbor(user)
        # print 'nearest=%s'%nearest
        #
        # now get the ratings for the user
        #
        userRatings = self.data[user]
        #
        # determine the total distance
        totalDistance = 0.0
        for i in range(self.k):
            totalDistance += nearest[i][1]

        # print 'totalDistance=%s'%totalDistance
        # now iterate through the k nearest neighbors
        # accumulating their ratings
        for i in range(self.k):
            # compute slice of pie
            if totalDistance != 0:
                weight = nearest[i][1] / totalDistance
            else:
                weight = 0

            # print 'weight=%s'%weight
            # get the name of the person
            name = nearest[i][0]
            # get the ratings for this person
            neighborRatings = self.data[name]
            # print 'neighborRatings=%s'%neighborRatings
            # print 'userRatings=%s'%userRatings
            # get the name of the person
            # now find bands neighbor rated that user didn't
            for artist in neighborRatings:
                if not artist in userRatings:
                    if artist not in recommendations:
                        recommendations[artist] = (neighborRatings[artist]
                                                   * weight)
                    else:
                        recommendations[artist] = (recommendations[artist]
                                                   + neighborRatings[artist]
                                                   * weight)
        # now make list from dictionary
        # print 'recommendations=%s'%recommendations.items()
        #recommendations = list(recommendations.items())

        #recommendations = [(self.convertProductID2name(k), v)
                           #for (k, v) in recommendations]
        # finally sort and return
        #recommendations.sort(key=lambda artistTuple: artistTuple[1],
                             #reverse=True)
        # Return the first n items
        return recommendations

    def saveDb(self ,value):
        try:
            conn = MySQLdb.connect(host='120.77.249.112', user='root', passwd='7f795ee0da', port=3306)
            cur = conn.cursor()
            conn.select_db('test_cengfan7')
            #check
            count = cur.execute('select uid,kit_ids from c_kitchen_recommend WHERE uid = %s'%value[0])

            print  count
            if count == 0:

                print 'add doing...'
                #add
                # add
                add_ok = cur.execute('insert into c_kitchen_recommend values(%s,%s)', value)
                if add_ok:
                    print 'add ok'
                    conn.commit()
                else:
                    print 'add fail'

                return  0


            #update
            exist = cur.fetchone()

            if  exist[1] == value[1] :
                print 'next...'
                return 0

            print 'update doing...'

            if count == 1:
                #update
                sql =  'update c_kitchen_recommend set kit_ids="%s"  where uid=%s' % (value[1], value[0])
                update_ok = cur.execute(sql)

                if update_ok:
                    print 'update ok'
                    conn.commit()
                else:
                    print 'update fail....'

            cur.close()
            conn.close()


        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])


if __name__ == '__main__':
    r = recommender([],6)
    #r.loadBookDB("./online/")
    # r.loadBookDB("./")
    r.loadBookDB2('test_cengfan7','120.77.249.112','root','7f795ee0da')

    # list = r.recommend('210')
    # print 'list='
    # print list

    for u in r.userid2name:

        # print u
        list = r.recommend(u)
        if list :
            print 'uid=%s, list=%s'%(u,list)
            l = list.keys()
            item = ','.join(str(e) for e in l)
            print item
            r.saveDb([u,item])
            # print '%s' %list

