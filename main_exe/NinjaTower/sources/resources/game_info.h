#include <vector>
#include <string>

using namespace std;
#pragma once
class game_player
{
	public:
		int pid;
		string login;
		int team;
		string char_name;
};

class game_info
{
	public:
		string name_map;
		string challenge;
		int me;
		vector<game_player> game_players;
};