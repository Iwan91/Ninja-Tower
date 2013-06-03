#include "input.h"
#include "../sockets/communication.h"
#include "../logger.h"
input::input()
{
}

input& input::getInstance()
{
          //Inicjalizacja statycznego obiektu.
          //Obiekt zostanie utworzony przy pierwszym wywo³aniu tej metody
          //i tylko wtedy nast¹pi inicjalizacja przy pomocy konstruktora.
          //Ka¿de nastêpne wywo³anie jedynie zwróci referencjê tego obiektu.
          static input instance;
          return instance;
}

keyboard::keyboard()
{
	keyclear();
}
void keyboard::keyclear()
{
	memset(key, 0, sizeof(*key)*256);
}

void keyboard::keydown(ALLEGRO_KEYBOARD_EVENT *kb) 
{
	if(key[kb->keycode]==KEYPRESSED)
	{
		keyrepeat(kb);
	}
	else
	{
		key[kb->keycode] = KEYPRESSED | KEYNEW;
	}

	change=true;
}

void keyboard::keyup(ALLEGRO_KEYBOARD_EVENT *kb) 
{
	key[kb->keycode] &= ~KEYPRESSED;

	change=true;
}

void keyboard::keyrepeat(ALLEGRO_KEYBOARD_EVENT *kb) 
{
	key[kb->keycode] |= KEYREPEAT;
}

void keyboard::keyupdate() 
{
	int i;
	static int val = ((KEYNEW | KEYREPEAT) << 24) 
			       | ((KEYNEW | KEYREPEAT) << 16) 
			       | ((KEYNEW | KEYREPEAT) << 8)  
			       |   KEYNEW | KEYREPEAT;
 
	for(i=0; i<64; i++) ((int*)key)[i] &= ~val;
}

void keyboard::keycheck()
{
	SendMoveStatus();
}

void keyboard::SendMoveStatus()
{
	logger::Write("keyboard::SendMoveStatus()-start",logger::level::debug);

	if(change==true)
	{
		unsigned char paczka[2];
		paczka[0] = 0;
		paczka[1] = key[ALLEGRO_KEY_W] + (key[ALLEGRO_KEY_A] << 1) + (key[ALLEGRO_KEY_D] << 2) + (key[ALLEGRO_KEY_S] << 3);
		string pakiet_do_wyslania((const char *)paczka, 2);
		communication::getInstance().SendTCP(pakiet_do_wyslania);
		logger::Write("input send data(TCP): "+pakiet_do_wyslania,logger::level::info);
		change=false;
	}

	logger::Write("keyboard::SendMoveStatus()-end",logger::level::debug);

}

void input::SendActionKey()
{
	logger::Write("input::SendActionKey()-start",logger::level::debug);

	engine &eng=engine::getInstance();
	resources &res = resources::getInstance();
	if(eng.heroes_simulation[res.game_info.me]->animation_intercept_true!=true)
	{
		unsigned char paczka[8];
		paczka[0]=1;

		unsigned short x=input::getInstance().mouse.x;
		unsigned short y=input::getInstance().mouse.y;
		unsigned short p=0;

		paczka[2] = x & 0xFF;
		paczka[3] = (x>>8) & 0xFF;
		paczka[4] = y & 0xFF;
		paczka[5] = (y>>8) & 0xFF;
		paczka[6] = p & 0xFF;
		paczka[7] = (p>>8) & 0xFF;

		if(mouse.key[1]==1 && eng.heroes_simulation[res.game_info.me]->cds[0]<=200)//LPM
		{
			paczka[1]=3;
			string pakiet_do_wyslania((const char *)paczka, 8);
			communication::getInstance().SendTCP(pakiet_do_wyslania);
		}

		if(mouse.key[2]==1 && eng.heroes_simulation[res.game_info.me]->cds[1]<=200)//PPM
		{
			paczka[1]=4;
			string pakiet_do_wyslania((const char *)paczka, 8);
			communication::getInstance().SendTCP(pakiet_do_wyslania);
		}

		if(keyboard.key[ALLEGRO_KEY_LSHIFT]==1 && eng.heroes_simulation[res.game_info.me]->cds[2]<=200)
		{
			paczka[1]=2;
			string pakiet_do_wyslania((const char *)paczka, 8);
			communication::getInstance().SendTCP(pakiet_do_wyslania);
		}

		if(keyboard.key[ALLEGRO_KEY_Q]==1 && eng.heroes_simulation[res.game_info.me]->cds[3]<=200) 
		{
			paczka[1]=0;
			string pakiet_do_wyslania((const char *)paczka, 8);
			communication::getInstance().SendTCP(pakiet_do_wyslania);
		}

		if(keyboard.key[ALLEGRO_KEY_E]==1 && eng.heroes_simulation[res.game_info.me]->cds[4]<=200)
		{
			paczka[1]=1;
			string pakiet_do_wyslania((const char *)paczka, 8);
			communication::getInstance().SendTCP(pakiet_do_wyslania);	
		}
		
	}

	logger::Write("input::SendActionKey()-end",logger::level::debug);

}

void mouse::keydown(ALLEGRO_MOUSE_EVENT *km)
{
	key[km->button]=1;
}

void mouse::keyup(ALLEGRO_MOUSE_EVENT *km)
{
	key[km->button]=0;
}
