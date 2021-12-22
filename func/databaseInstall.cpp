#include <string>
#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <hiredis/hiredis.h>
using namespace std;

redisContext* conn;
string path;

void readAtrribute(){
    int line  = 1;
    char pnode[10],attr[10];
    fstream fin(path + "/attribute.txt");
    redisReply* reply = (redisReply*)redisCommand(conn,"select 1");
    freeReplyObject(reply);
    reply = (redisReply*)redisCommand(conn,"flushdb");
    freeReplyObject(reply);
    while(fin>>pnode){
        fin>>attr;
        reply = (redisReply*)redisCommand(conn,"select 1");
        freeReplyObject(reply);
        reply = (redisReply*)redisCommand(conn,"sadd %s %s",pnode,attr);
        freeReplyObject(reply);
        //cout<<"pnode:"<<pnode<<"attr:"<<attr<<endl;
    }
    fin.close();
}

void readRelation(){
    char pnode[10],cnode[10];
    fstream fin(path + "/relation.txt");
    redisReply* reply = (redisReply*)redisCommand(conn,"select 2");
    freeReplyObject(reply);
    reply = (redisReply*)redisCommand(conn,"flushdb");
    freeReplyObject(reply);
    while(fin>>cnode){
        fin>>pnode;
        reply = (redisReply*)redisCommand(conn,"select 2");
        freeReplyObject(reply);
        reply = (redisReply*)redisCommand(conn,"sadd %s %s",pnode,cnode);
        freeReplyObject(reply);
        reply = (redisReply*)redisCommand(conn,"select 3");
        freeReplyObject(reply);
        reply = (redisReply*)redisCommand(conn,"sadd %s %s",cnode,pnode);
        freeReplyObject(reply);
    }
    fin.close();
}

int main(int argc, char *argv[]){
    path = argv[1];
    conn = redisConnect("127.0.0.1",6379);
    readAtrribute();
    cout<<"read attribute over!!!!!"<<endl;
    readRelation();
    cout<<"read relation over!!!!!"<<endl;
    redisFree(conn);
    return 0;
}