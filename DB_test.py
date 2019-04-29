# coding:utf-8
from threading import Thread
import thread
import Source as s
import DB
import M


def s():
    t1 = Thread(target = sss,args = (10,0))
    t1.setDaemon(True)
    print("222:",333)
    t1.start()
    
def sss(intInterval):
    t = s.Timing()
    db = DB.SANSW()
    def do_it():
        print("132321:",3333)
        db.insert(n,self.get_SANSW_origin,self.show_SANSW_error,get_SANSW_summary)
    t.add_interval(do_it)
    t.sss

if __name__ == '__main__':
    s()