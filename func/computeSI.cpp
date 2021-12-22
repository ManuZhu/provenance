#include<iostream>
#include<fstream>
#include<stdlib.h>
#include<algorithm>
#include<set>
#include<iterator>
#include<string.h>
#include<string>
#include<vector>
#include<hiredis/hiredis.h>

using namespace std;

redisContext* conn;
std::vector<int>vH;
std::vector<int>vA;
std::set<int>circlepoint;            //自指节点
string path;

//获取所有Des
void getAllDestinations(char * pnode, std::vector<int>& temp)
{
        redisReply* reply = (redisReply*)redisCommand(conn,"select 2");
        freeReplyObject(reply);
        reply = (redisReply*)redisCommand(conn,"smembers %s",pnode);
        for(int i = 0 ;i < reply->elements;i++)
        {
                temp.push_back(atoi(reply->element[i]->str));
               // cout<<"dest"<<atoi(reply->element[i]->str)<<" ";
        }
}


//修改H和SI值
void update_vertex_H_SI(int id, int H, int A,double &SInum)
{
	double SI = A*0.375 + H*0.625;
	SInum += SI;
	char *pnode = new char;
	char *nodeSI = new char;
	sprintf(pnode,"%d",id);
	sprintf(nodeSI,"%f",SI);
	redisReply* reply = (redisReply*)redisCommand(conn,"select 4");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"set %s %s",pnode,nodeSI);
	freeReplyObject(reply);
	std::cout << "更新" << id << "的H值" << H <<" "<<"的A值"<< A << " " << "SI值" << SI << std::endl;
}

void state_calculate(int i)
{
        double xishu = 1.0 * i / vH.size();
        int fint = (int)(xishu * 10);
        std::cout << "已完成：";
        for (int i = 0;i < fint;i++)
                std::cout << "*";
        std::cout << (int)(xishu * 100) << "%" << std::endl;
}


//将所有节点的H、SI写回数据库
void update_sql_H_ST()
{
	double SInum = 0;
	for (int i = 0; i < vH.size(); i++)
	{
		update_vertex_H_SI(i + 1, vH[i], vA[i],SInum);
		if (i % 100 == 0)
		{
			state_calculate(i);
		}
	}
	ofstream os(path + "/nodeSIsum.txt");
	std::string temp = std::to_string(SInum);
	cout<<"SI总值"<<SInum<<endl;
	int len = temp.length() + 1;
	char* arr = new char[len];
	sprintf(arr, "%.1f", SInum);
	os<<arr<<endl;
	os.close();
	std::cout << "写回H_SI完成" << std::endl;
}


void getAllCircle()//获取Circle节点
{
	fstream fin(path + "/relation.txt");
	char *pnode = new char;
	char *cnode = new char;
	while(fin>>pnode)
	{
		fin>>cnode;
		if(atoi(pnode) == atoi(cnode))
			circlepoint.insert(atoi(pnode));
	}
	fin.close();
}

//获取所有节点A值,初始化H值
void getAllPoint()
{
	fstream fin(path + "/attribute.txt");
    char *node = new char;
	char *A = new char;
    while(fin>>node){
        fin>>A;
		vA.push_back(atoi(A));
		vH.push_back(0);
    }
    fin.close();
}

//获取点的所有子节点
void get_from(char pnode[20], std::vector<int>& fro)
{
	redisReply* reply = (redisReply*)redisCommand(conn,"select 2");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"smembers %s",pnode);
	for(int i = 0 ;i < reply->elements;i++)
	{
		fro.push_back(atoi(reply->element[i]->str));
		cout<<"child"<<atoi(reply->element[i]->str)<<" ";
	}
}

//计算一个节点的H值
int compute_H_one(int no, std::vector<int>& buffer)
{
	int h = vH[no - 1];
	if (h != 0)
		return h;
	std::vector<int>::iterator iter = std::find(buffer.begin(), buffer.end(), no);
	if (iter != buffer.end())
		return 0;
	buffer.push_back(no);
	std::vector<int>des;
	char *pnode = new char;
	sprintf(pnode,"%d",no);
	getAllDestinations(pnode, des);
	//std::cout << "第" << no << " " << des.size ();
	std::set<int>::iterator it = circlepoint.end();
	if(circlepoint.size() > 0)
	    	it = std::find(circlepoint.begin(),circlepoint.end(),no);
	long long int sum;
	//判断是否为自指环
	if (it == circlepoint.end())
		sum = 1;
	else
	{
		sum = 0;
	}
	for (int i = 0; i < des.size();i++)
	{
		sum += compute_H_one(des[i], buffer);
	}
	iter = std::find(buffer.begin(), buffer.end(), no);
	buffer.erase(iter);
	vH[no - 1] = sum;
	return sum;
}

void compute_H()
{
	std::vector<int>buffer;
	for (int i = 0; i < vH.size() - 1;i++)
	{
		
		if (vH[i] == 0)
		{
			compute_H_one(i + 1, buffer);
		}

		if (i % 100 == 0)
		{
			state_calculate(i);
		}
	}
	std::cout << "计算H值完成" << std::endl;

}


void getnodeSI(char *pnode ,double &SI){
    redisReply* reply = (redisReply*)redisCommand(conn,"select 4");
    freeReplyObject(reply);
    reply = (redisReply*)redisCommand(conn,"get %s",pnode);
    if(reply->type == REDIS_REPLY_NIL){
        SI = -1;
        freeReplyObject(reply);
    }
    else{
        SI = atof(reply->str);
        freeReplyObject(reply);
    }
}

void printnodeD(){
    redisReply* reply = (redisReply*)redisCommand(conn,"select 4");
    freeReplyObject(reply);

    reply = (redisReply*)redisCommand(conn,"keys *");
    std::vector<double>vSI(reply->elements);
    
    for(int i = 0; i < reply->elements; i++){
        double nodeSI;
        getnodeSI(reply->element[i]->str,nodeSI);
        vSI[atoi(reply->element[i]->str)-1] = nodeSI;
    }
    freeReplyObject(reply);

    int len = vSI.size();
    ofstream os(path + "/nodeDisplay.txt");
    for(int i = 0;i < len; i++){
        os<<i+1<<" ";
        os<<vSI[i]<<endl;
    }
    os.close();
}

void init()
{
	redisReply* reply = (redisReply*)redisCommand(conn,"select 4");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"flushdb");
	freeReplyObject(reply);
}

int main(int argc, char *argv[])
{
    path = argv[1];
    conn = redisConnect("127.0.0.1",6379);
    init();
	getAllCircle();
	getAllPoint();
	compute_H();    //计算所有节点的H和SI值
	update_sql_H_ST();
	printnodeD();
	redisFree(conn);
}