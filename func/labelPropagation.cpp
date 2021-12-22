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

struct new_node{
	int id;
	double SI;
	int label;
	new_node(int id, double SI,double label){
		this->id = id;
		this->SI = SI;
		this->label = label;
	}
};

int nodeNum;
double nodeSINum;
double threshold;
double curnodeSINum;
redisContext* conn;
std::vector<new_node> labels;
string path;

bool cmp(new_node &a , new_node &b){//SI值从大到小，编号从小到大
	return a.SI == b.SI ? a.id < b.id : a.SI > b.SI;
}

void getAllDestinations(char *pnode, std::vector<int>& temp){
	redisReply* reply = (redisReply*)redisCommand(conn,"select 2");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"smembers %s",pnode);
	for(int i = 0 ;i < reply->elements;i++){
		temp.push_back(atoi(reply->element[i]->str));
		//cout<<"dest"<<atoi(reply->element[i]->str)<<" ";
	}
}

void getAllSources(char *pnode, std::vector<int>& temp){
	redisReply* reply = (redisReply*)redisCommand(conn,"select 3");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"smembers %s",pnode);
	for(int i = 0 ;i < reply->elements;i++){
		temp.push_back(atoi(reply->element[i]->str));
		//cout<<"dest"<<atoi(reply->element[i]->str)<<" ";
	}
}

//判断是否被标记
bool hasLabeled(char *pnode){
	redisReply* reply = (redisReply*)redisCommand(conn,"select 5");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"get %s",pnode);
	if(reply->type == REDIS_REPLY_NIL){
		freeReplyObject(reply);
		return false;
	}
	else{
		freeReplyObject(reply);
		return true;
	}
}

void getnodeSI(char *pnode ,double &SI){
	//cout<<"here";
	redisReply* reply = (redisReply*)redisCommand(conn,"select 4");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"get %s",pnode);
	if(reply->type == REDIS_REPLY_NIL){
		SI = -1;
		freeReplyObject(reply);
	}
	else{
		//cout<<pnode<<"SI值为"<<atof(reply->str)<<endl;
	 	SI = atof(reply->str);
		freeReplyObject(reply);
	}
}

//设置初始标签[降序写入]，对于节点SI值大于阈值的节点，将节点和与其连通的节点标签值定义为该节点的编号值。
void read_node_SI(std::vector<new_node>& labels){

	std::vector<int> vid;
	std::vector<int> vlabel;
	std::vector<double> vSI;
	std::vector<new_node> tempnode;

	redisReply* reply = (redisReply*)redisCommand(conn,"select 4");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"keys *");

	for(int i = 0; i < reply->elements; i++){//将还没有设置标签且si值大于等于门限值的节点加入tempnode，标签值设为0
		//cout<<i<<" ";
		//cout<<reply->element[i]->str<<endl;
		double nodeSI;
	    getnodeSI(reply->element[i]->str,nodeSI);
		if(nodeSI >= threshold && !hasLabeled(reply->element[i]->str)){
			//cout<<"nowword"<<atoi(reply->element[i]->str)<<" "<<nodeSI<<endl;
			tempnode.push_back(new_node(atoi(reply->element[i]->str), nodeSI, 0));
		}	
	}
	freeReplyObject(reply);

	sort(tempnode.begin(),tempnode.end(),cmp);//按照si值从大到小，编号值从小到大排序
	for(int i = 0 ; i < tempnode.size();i++){
		vid.push_back(tempnode[i].id);
		vSI.push_back(tempnode[i].SI);
		vlabel.push_back(0);
	}

	for (int i = 0; i < vid.size(); i++){
		if (vlabel[i] == 0){
            //std::cout << "初始设置" << vid[i]<< std::endl;
			vlabel[i] = vid[i];

			char *tempid = new char;
			sprintf(tempid,"%d",vid[i]);

			std::vector<int>temp;
			getAllDestinations(tempid, temp);
			getAllSources(tempid, temp);

			for (int j = 0; j < temp.size(); j++){
				std::vector<int>::iterator it = find(vid.begin(), vid.end(), temp[j]);//如果和tempid联通的节点在tempnode中，则将其标签设置为当前节点编号
				if (it != vid.end()){
					vlabel[std::distance(vid.begin(), it)] = vid[i];
				}
			}
		}
		//std::cout << "初始设置" << vid[i] << std::endl;
		labels.push_back(new_node(vid[i], vSI[i], vlabel[i]));//将设置好标签值的节点加入labels
		//write_node_label(mysql, vid[i], vlabel[i]);
	}
	return;
}

int get_label(int id){
	for (int i = 0; i < labels.size();i++){
		if (labels[i].id == id)
			return labels[i].label;
	}
	return -1;
}

void set_label(int id, int label){
	for (int i = 0; i < labels.size();i++){
		if (labels[i].id == id){
			labels[i].label = label;
			break;
		}
	}
}

void write_node_label(int id, int nowlabel){
	char *pnode = new char;
	char *label = new char;
	sprintf(pnode,"%d",id);
	sprintf(label,"%d",nowlabel);
	redisReply* reply = (redisReply*)redisCommand(conn,"select 5");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"set %s %s",pnode,label);
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"select 6");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"sadd %s %s",label,pnode);
	freeReplyObject(reply);
	
	ofstream os(path + "/nodeLabel.txt",ios_base::app);
	os<<pnode<<" ";
	os<<label<<endl;
	os.close();
	//std::cout << "写入节点" << id << "label值" << nowlabel<<endl;
}

//一次标签传播
int spread_label_one(int lab, int id, std::vector<new_node>& temp_label){
	//?????????????if(lab == 0 || lab == -1) return 0;
	//label为0表示加入了labels但还没有值，-1表示还没有加入labels

	int sum = 0;
	std::vector<int> temp;
	char *pnode = new char;
	sprintf(pnode,"%d",id);
	getAllSources(pnode, temp);
	getAllDestinations(pnode, temp);

	for(int i = 0; i < temp.size(); i++){

		int label = get_label(temp[i]);
		//??????????????if (label == 0 || label == -1){
		if (label == -1){

			char *tempnode = new char;
			sprintf(tempnode,"%d",temp[i]);
			double SI;
		    getnodeSI(tempnode,SI);

			if (label == 0){
				set_label(temp[i], lab);
			}
			else{
				labels.push_back(new_node(temp[i], SI, lab));
			}
			//write_node_label(mysql, temp[i], lab);
			temp_label.push_back(new_node(temp[i], SI, lab));
			//std::cout << "设置id为" << temp[i] << "的lab值为" << lab << std::endl;
			sum++;
		}
	}
	return sum;
}

int spread_label_once(){
	read_node_SI(labels);
	int sum = labels.size();

	if (labels.size() > 0){

		std::vector<new_node> oldque;
		std::vector<new_node> tempque;

		for (int i = 0; i < labels.size(); i++){
			sum += spread_label_one(labels[i].label, labels[i].id, tempque);
		}

		int sumonce;
		do{
			sumonce = 0;
			sort(tempque.begin(), tempque.end(), cmp);
			while (!oldque.empty()) oldque.pop_back();

			for (int i = 0; i < tempque.size(); i++){
				oldque.push_back(new_node(tempque[i].id, tempque[i].SI, tempque[i].label));
			}
			while (!tempque.empty()) tempque.pop_back();

			for (int i = 0; i < oldque.size(); i++){
				sumonce += spread_label_one(oldque[i].label,oldque[i].id, tempque);
			}
			sum += sumonce;
		}while (sumonce != 0);

		for (int i = 0; i < labels.size(); i++){
			curnodeSINum += labels[i].SI;
			write_node_label(labels[i].id, labels[i].label);
		}
	}
	return sum;
}

int main(int argc, char *argv[]){
	path = argv[1];
	conn = redisConnect("127.0.0.1",6379);
	redisReply* reply = (redisReply*)redisCommand(conn,"select 5");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"flushdb");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"select 6");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"flushdb");
	freeReplyObject(reply);
	int sum = 0;

	char *thre = new char;
	ifstream fin(path + "/nodeSIsum.txt");
	fin>>thre;
	fin.close();
	reply = (redisReply*)redisCommand(conn,"select 4");
	freeReplyObject(reply);
	reply = (redisReply*)redisCommand(conn,"keys *");
	nodeNum = reply->elements;
	nodeSINum = atof(thre);
	threshold = nodeSINum / nodeNum * 1.2;

	vector<double>take_time;
	clock_t starttime, endtime;

	do{
		std::cout << "当前阈值" << threshold << std::endl;
		while (!labels.empty())  labels.pop_back();

		cout<<"here"<<endl;
        starttime = clock();
		sum = spread_label_once();
		endtime = clock();
		double totaltime = (double)( (endtime - starttime)/(double)CLOCKS_PER_SEC );
		take_time.push_back(totaltime);

		std::cout << "一共处理" << sum << "个节点" << std::endl;
		nodeNum -= sum;
		if(nodeNum == 0) break;
		threshold = (nodeSINum - curnodeSINum) / nodeNum * 1.2;

	}while (sum > 0 && threshold > 0);

	for(int i = 0;i < take_time.size();i++) cout<<take_time[i]<<" ";
	cout<<endl;

	redisFree(conn);
	return 0;
}