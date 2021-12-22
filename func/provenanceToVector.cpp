#include<iostream>
#include<fstream>
#include<stdio.h>
#include<queue>
#include<stack>
#include<set>
#include<math.h>
#include<stdlib.h>
#include<algorithm>
#include<iterator>
#include<string.h>
#include<string>
#include<vector>
#include<hiredis/hiredis.h>
using namespace std;

struct SNode{
	int id;
	double SI;
	SNode(int i, double s){
		this->id = i;
		this->SI = s;
	}
};

struct VNode {
	double SI;
	int distance;
	VNode(double si, int dis){
		this->SI = si;
		this->distance = dis;
	}
	bool operator == (const VNode& newvnode){
		return SI == newvnode.SI && distance == newvnode.distance;
	}

};

int K = 16;

vector<int>Lable;                              //获取所有的标签值
vector<SNode> centernode;                      //中心节点
redisContext* conn;
string path, vectorAddress;

bool cmp(SNode& node1, SNode& node2){
	return node1.SI > node2.SI;
}

int getNumberofNode(char *label){
	redisReply* reply = (redisReply*)redisCommand(conn,"select 6");// 遍历数据库6
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"smembers %s",label);
	return reply->elements;
}

double getSI(char *pnode){
	//cout<<"here";
	redisReply* reply = (redisReply*)redisCommand(conn,"select 4");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"get %s",pnode);
	if(reply->type == REDIS_REPLY_NIL){
		freeReplyObject(reply);
		return -1;
	}
	else{
		double SI = atof(reply->str);
		//cout<<pnode<<"SI值为"<<SI<<endl;
        freeReplyObject(reply);
	 	return  SI;
	}
}

void getCenterNode(char *label){//获取每个事件的中心节点
	while(!centernode.empty()) centernode.pop_back();

	redisReply* reply = (redisReply*)redisCommand(conn,"select 6");//遍历数据库6
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"smembers %s",label);
	for(int i = 0; i < reply->elements; i++){
		centernode.push_back(SNode(atoi(reply->element[i]->str) , getSI(reply->element[i]->str)));
	}

	sort(centernode.begin(),centernode.end(),cmp);
	while(centernode.size() > K)  centernode.pop_back();

	if(centernode.size() < K){
		for(int i = centernode.size(); i < K; i++){
			centernode.push_back(SNode(0, 0.0));
		}
	}
	/*os<<"center node: ";
	for(int i = 0; i  < centernode.size(); i++)
	    os<<centernode[i].id<<" "<<centernode[i].SI<<endl;*/
	freeReplyObject(reply);
}

int getLabel(char * pnode){
	redisReply* reply = (redisReply*)redisCommand(conn,"select 5");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"get %s",pnode);
	if(reply->type == REDIS_REPLY_NIL){
		freeReplyObject(reply);
		return -1;
	}
	else{
		//cout<<pnode<<"SI值为"<<atof(reply->str)<<endl;
        int  label = atoi(reply->str);
        freeReplyObject(reply);
	 	return label;
	}
}

void getFromTo(int id, vector<SNode>& tempnode, int label){//获取节点的邻接节点
	char *pnode = new char;
	sprintf(pnode, "%d", id);

	char *plabel = new char;
	sprintf(plabel, "%d", label);

	redisReply* reply = (redisReply*)redisCommand(conn,"select 2");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"smembers %s",pnode);
	for(int i = 0;i < reply->elements; i++){
		if(getLabel(reply->element[i]->str) == label)
			tempnode.push_back(SNode(atoi(reply->element[i]->str),getSI(reply->element[i]->str)));
	}
	freeReplyObject(reply);

	reply = (redisReply*)redisCommand(conn,"select 3");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"smembers %s",pnode);
	for(int i = 0;i < reply->elements; i++){
		if(getLabel(reply->element[i]->str) == label)
			tempnode.push_back(SNode(atoi(reply->element[i]->str),getSI(reply->element[i]->str)));
	}
	freeReplyObject(reply);
}

void writefir(vector<VNode>& tempvnode){
	FILE* fp;
	//cout << "写入" << Macro::vectoraddress << endl;
	if ((fp = fopen(vectorAddress.c_str(), "a+")) == NULL){
		cout << "open vectoraddress-node.txt error" << endl;
		exit(1);
	}
	for (int i = 0 ; i < tempvnode.size() && i < K ; i++){
		//cout << tempvnode[i].SI << " ";
		std::string temp = std::to_string(tempvnode[i].SI);
		//cout << temp << " ";
		int len = temp.length() + 1;
		char* arr = new char[len];
		sprintf(arr, "%.2f", tempvnode[i].SI);
		fputs(arr, fp);
		fputs(" ", fp);
		delete[]arr;
	}
	if(tempvnode.size() < K){//补零操作
		for(int i = tempvnode.size(); i < K; i++){
			fputs("0.0", fp);
			fputs(" ", fp);
		}
	}
	fclose(fp);
	//cout << endl;
}

void writelable(vector<VNode>& tempvnode){//写入事件标签
	FILE* fp;
	//cout << "写入" << endl;
	if((fp = fopen(vectorAddress.c_str(), "a+")) == NULL){
		cout << "open vectoraddress-node.txt error" << endl;
		exit(1);
	}
	for(int i = 0; i < tempvnode.size() && i < K; i++){
		std::string temp = std::to_string(tempvnode[i].SI);
		//cout << temp << " ";
		int len = temp.length() + 1;
		char* arr = new char[len];
		sprintf(arr, "%.1f", tempvnode[i].SI);
		fputs(arr, fp);
		fputs(" ", fp);
		delete[]arr;
	}
	if (tempvnode.size() < K){//补零操作
		for (int i = tempvnode.size(); i < K; i++){
			fputs("0.0", fp);
			fputs(" ", fp);
		}
	}
	fputs("1 0 ",fp);
	fputs("\t\n", fp);
	//cout<<endl;
	fclose(fp); 
}

void getNeighbOne(int id ,double si,int la,int label,bool first){//获取一个节点的邻域
	FILE* fp;
	fp = fopen((path + "/nodeVector.txt").c_str(), "a+");
	//cout << si << " ";
	int number = 1;
	int distance = 1;
	vector<int>writenodeid;
	vector<VNode>writenode;
	
	if(id == 0){
		for(int i = 0; i < K; i++) writenode.push_back(VNode(0.0, 0));
		if (la == 1) writefir(writenode);
		else writelable(writenode);
	}
	else{
		writenodeid.push_back(id);
		writenode.push_back(VNode(si, 0));//首先写入中心节点

		queue<int>oldnode;
		oldnode.push(id);
		while(!oldnode.empty() && number < K){
			vector<SNode>addnode;
			while(!addnode.empty()) addnode.pop_back();
			while(!oldnode.empty()){
				int oldid = oldnode.front();
				oldnode.pop();
				vector<SNode> tempnode;
				getFromTo(oldid, tempnode, label);//获取邻接节点标签值和中心节点一致的节点
				for (int i = 0; i < tempnode.size(); i++){
					addnode.push_back(SNode(tempnode[i].id, tempnode[i].SI));
				}
			}
			sort(addnode.begin(), addnode.end(), cmp);
			for(int i = 0; i < addnode.size(); i++){
				vector<int>::iterator it;
				if((it = find(writenodeid.begin(), writenodeid.end(), addnode[i].id)) == writenodeid.end()){
					//cout << addnode[i].SI << " ";
					number++;
					oldnode.push(addnode[i].id);
					writenodeid.push_back(addnode[i].id);
					writenode.push_back(VNode(addnode[i].SI, distance));
				}
			}
			distance++;
		}

		if(writenode.size() > 2 * K){//邻域规范化
			//cout<<id<<"need normalize"<<endl;

			int m, j = 0, p = 0;
			double high = 1.0, conv = 0;
			vector<double>conKernel;

			for(m = 0; m < writenode.size() - 2 * K; m++){
				//srand(time(0));
				double rate = high * ((rand() % 100) / (double)100);
				conKernel.push_back(rate);
				high -= rate;
			}

			conKernel.push_back(high);
			sort(conKernel.begin(),conKernel.end(),greater<double>());

			while(p < K){
				j = 0, m = p, conv = 0;
				while(j < writenode.size() - 2 * K + 1){
					conv += writenode[m].SI * conKernel[j];
					m++;
					j++;
				}
				writenode[p].SI = conv;
				p++;
			}
		}
		if (first){
			for(int i = 0; i < writenodeid.size() && i < K; i++){
				fprintf(fp, "%d\n", writenodeid[i]);
			}
			if (writenodeid.size() < K){
				for (int i = writenodeid.size(); i < K; i++){
					fprintf(fp, "0\n");
				}
			}
		}
		if (la == 1) writefir(writenode);
		else writelable(writenode);
	}
	fclose(fp);
}

int main(int argc, char *argv[]){//获取所有中心节点的邻域
	path = argv[1];
	vectorAddress = path + "/nodeAddress.txt";
	conn = redisConnect("127.0.0.1",6379);
	redisReply* reply = (redisReply*)redisCommand(conn,"select 6");// 遍历数据库6
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"keys *");
	if(reply->type != REDIS_REPLY_ARRAY){
		cout<<"select * from database 6 error"<<endl;
	}
	if(reply->elements == 0){
		cout<<"database 6 empty"<<endl;
	}
	for(int i=0;i<reply->elements;i++){
		int nowlabel = atoi(reply->element[i]->str);
		//cout<<getNumberofNode(reply->element[i]->str)<<endl;
        if(getNumberofNode(reply->element[i]->str) < 6){
			//os<<"quit"<<endl;
			continue;
		}
		else{
			//os<<"lable值: "<<nowlabel<<endl;
			char *nowlabelstr = new char;
			sprintf(nowlabelstr , "%d" , nowlabel);
			getCenterNode(nowlabelstr);
			bool first = 1;
			for (int j = 0; j < centernode.size();j++){
				//os<<"centernode: "<<centernode[j].id<<endl;
				if (j < centernode.size() - 1)
					getNeighbOne(centernode[j].id, centernode[j].SI, 1, nowlabel, first);
				else
					getNeighbOne(centernode[j].id, centernode[j].SI, 0, nowlabel, first);
				first = 0;
	     	}
		}
	}
	redisFree(conn);
	return 0;
}