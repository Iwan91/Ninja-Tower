#include <iostream>
#include <string>
#include <vector>
using namespace std;
#pragma once
class hero_simulation
{
	public:
		int id_resource;

		double hero_x;
		double hero_y;
		double hero_x_relative;
		double hero_y_relative;
		double dy,dx;
		int hp_now;

		vector<int> cds;

		struct animation
		{
			int frame_display;
			int id_animation;
			int frame_delay;
			int frame_count;
			bool change_animation;
		};

		animation Animation;
		animation Animation_intercept;

		bool animation_intercept_true;

		bool dead;
		int down_up;
};