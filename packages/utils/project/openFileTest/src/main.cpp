#include <fstream>
#include <iostream>
#include <string>

using namespace std;

int main(int argc, char** argv)
{
	string cfgPath="cfg/*.json";
	for(int i=1;i<5;++i)
	{
		cout << cfgPath <<endl;
		std::ifstream ifs;
	        ifs.open(cfgPath.c_str());
        	if (ifs.is_open())
        	{
			cout << "open ok"<<endl;
        	}
	        else
        	{
			cout<< "fail"<<endl;
        	}
	}
	return 0;
}

