#include <iostream>
#include <string>
using namespace std;
#pragma once
class shot_simulation
{
	public:
		int id_resource;
		int sid;
		int tracked; //1- tracked,0- non-tracked
		double shot_x;
		double shot_y;
		double shot_x_relative;
		double shot_y_relative;
		double dy,dx;

		struct animation
		{
			int frame_display;
			int id_animation;
			int frame_delay;
			int frame_count;
			bool change;
			bool face;
			bool change_animation;
		}Animation;
};