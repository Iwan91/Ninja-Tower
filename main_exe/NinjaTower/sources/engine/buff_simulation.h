#include <iostream>
#include <string>
using namespace std;
#pragma once
class buff_simulation
{
	public:
		int ID_resource;
		unsigned short PID;
		unsigned short BID;
		unsigned char stacks;
		unsigned short expires;
};