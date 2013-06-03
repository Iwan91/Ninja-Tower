#include "communication.h"
#include "../logger.h"
#include "../resources/resources.h"
#include "../resources/game_info.h"
#include <algorithm>
communication::communication()
{

}
communication& communication::getInstance()
{
	//Inicjalizacja statycznego obiektu.
    //Obiekt zostanie utworzony przy pierwszym wywo³aniu tej metody
    //i tylko wtedy nast¹pi inicjalizacja przy pomocy konstruktora.
    //Ka¿de nastêpne wywo³anie jedynie zwróci referencjê tego obiektu.
	static communication instance;
	return instance;
}

void communication::SetConnection(string login, string password, string ip, string portTCP, string portUDP)
{
	this->login=login;
	this->password=password;
	this->ip=ip;
	this->portTCP=portTCP;
	this->portUDP=portUDP;
}

void communication::Connect()
{
	if(ConnectTCP_UDP()==false)
	{
		logger::Write("ConnectTCP_UDP() failed",logger::level::fatal_error);
		exit(0);
	}
	if(SecureTCP()==false)
	{
		logger::Write("SecureTCP() failed",logger::level::fatal_error);
		exit(0);
	}
}

bool communication::ConnectTCP_UDP()
{
	// Initialize Winsock.
	WSADATA wsaData;
	int iResult = WSAStartup(MAKEWORD(2,2), &wsaData);
	if (iResult != NO_ERROR)
		logger::Write("Client: Error at WSAStartup()",logger::level::fatal_error);
	else
		logger::Write("Client: WSAStartup() is OK",logger::level::debug);
	// Create a socket.
	//SOCKET m_socket;
	m_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (m_socket == INVALID_SOCKET)
	{
		logger::Write("Client: socketTCP() - Error at socket(): "+WSAGetLastError(),logger::level::fatal_error);
		WSACleanup();
		return 0;
	}
	else
		logger::Write("Client: socketTCP() is OK"+WSAGetLastError(),logger::level::debug);
	// Connect to a server.
	sockaddr_in clientService;
	clientService.sin_family = AF_INET;
	clientService.sin_addr.s_addr = inet_addr(ip.c_str());
	clientService.sin_port = htons((u_short)atoi(portTCP.c_str()));

	if (connect(m_socket, (SOCKADDR*)&clientService, sizeof(clientService)) == SOCKET_ERROR)
	{
		logger::Write("Client: connectTCP() - Failed to connect",logger::level::error);
		WSACleanup();
		return 0;
	}

	//ustawienia UDP
	UDP_socket=socket(AF_INET,SOCK_DGRAM,0);
	if(UDP_socket==INVALID_SOCKET)
	{
		logger::Write("Client: socketUDP() - Error at socket(): ",logger::level::fatal_error);
		return 0;
	}
	else
		logger::Write("Client: socketUDP() is OK",logger::level::debug);

	UDP_addr.sin_family=AF_INET;
	UDP_addr.sin_port=htons((u_short)atoi(portUDP.c_str()));
	UDP_addr.sin_addr.s_addr=inet_addr(ip.c_str());
	connect(UDP_socket, (SOCKADDR*)&UDP_addr, sizeof(UDP_addr));
	UDPNonBlocking(1);
	return 1;
}


void communication::TCPNonBlocking(DWORD nonBlocking)
{
	ioctlsocket(m_socket, FIONBIO, &nonBlocking );
}
void communication::UDPNonBlocking(DWORD nonBlocking)
{
	ioctlsocket(UDP_socket, FIONBIO, &nonBlocking );
}


string communication::ToLowerCase(string text)
{
	for(int i=0;i<text.length();i++)
	{
		text[i]=tolower(text[i]);
	}

	return text;
}
bool communication::SecureTCP()
{
	
	SendTCP(login);
	string w=ReceiveTCP();
	
	//hashlib.sha1(password_gracza + w).hexdigest()
	//string sha=GetSHA1(password+w);
	string sha=GetSHA1(GetSHA1(ToLowerCase(login)+password)+w);

	SendTCP(sha);
	string msg="";
	vector<string> split_msg;
	msg=ReceiveTCP();
	if(msg=="") return 0;

	split_msg=split(msg,'\xFF');
	resources::getInstance().game_info.name_map=split_msg[0];
	resources::getInstance().game_info.challenge=split_msg[1];

	msg=ReceiveTCP();
	if(msg=="") return 0;
	split_msg=split(msg,'\xFF');
	for(int i=0;i<split_msg.size();i++)
	{
		
		game_player Game_player;

		Game_player.pid=atoi(split_msg[i].c_str());
		Game_player.login=split_msg[i+1];
		Game_player.team=atoi(split_msg[i+2].c_str());
		Game_player.char_name=split_msg[i+3];

		resources::getInstance().game_info.game_players.push_back(Game_player);
		i=i+3;
	}

	for(int i=0;i<resources::getInstance().game_info.game_players.size();i++)
	{
		if(ToLowerCase(resources::getInstance().game_info.game_players[i].login)==ToLowerCase(login))
		{
			resources::getInstance().game_info.me=i;
			break;
		}
	}

	return 1;
}

void communication::SendTCP(string text2)
{
	try
	{
		if (text2.length() > 65535) throw "Too long packets";   
		unsigned short dlugosc_stringa = text2.length();  // short - 16 bit
		unsigned char * text_to_send = (unsigned char*)malloc(text2.length()+2);
				  
		text_to_send[0] = dlugosc_stringa >> 8;
		text_to_send[1] = dlugosc_stringa & 255;

		memcpy(text_to_send+2, text2.c_str(), dlugosc_stringa);
				
		send(m_socket, reinterpret_cast<const char*>(text_to_send), dlugosc_stringa+2, 0);

		logger::Write("Sending text TCP: "+text2,logger::level::info);

		ostringstream ss;
		ss <<"Sending text TCP: ";
		
		char temp_tab[2];
		for(int i=0;i<dlugosc_stringa+2;i++)
		{
			IntToHex((unsigned char)text_to_send[i], temp_tab);
			
			ss<<temp_tab[0] << temp_tab[1]<<" ";
		}
		logger::Write(ss.str(),logger::level::info);
		free(text_to_send);
	}
	catch (string exception)
	{
		logger::Write(exception,logger::level::error);
	}
}

string communication::ReceiveTCP()
{
	try
	{
		unsigned char rozmiar_pakietu_buf[2];
		unsigned short rozmiar_pakietu;

		int n=recv(m_socket,reinterpret_cast<char*>(rozmiar_pakietu_buf), 1,0);
		if(n>0)
		{
			recv(m_socket,reinterpret_cast<char*>(rozmiar_pakietu_buf+1), 1,0);

			rozmiar_pakietu = (rozmiar_pakietu_buf[0] << 8) + rozmiar_pakietu_buf[1];

			char * bufor =(char*) malloc(rozmiar_pakietu);
			int odebranych_danych = 0;

			while (odebranych_danych < rozmiar_pakietu) 
			{
				int t_odebranych_danych = recv(m_socket,bufor+odebranych_danych, rozmiar_pakietu-odebranych_danych,0);
				if (t_odebranych_danych == 0) throw "Server closed connection";
				odebranych_danych += t_odebranych_danych;
			}
			string result= string(bufor, rozmiar_pakietu);
			free(bufor);
			
			logger::Write("Reciving text TCP: "+result,logger::level::info);
			ostringstream ss;
			ss<<"Reciving text TCP: ";

			for(int i=0;i<result.length();i++)
			{
				ss<<hex<<(int)((unsigned char)result[i])<<" ";
			}
			logger::Write(ss.str(),logger::level::info);
			return result;
		}
		return "";
	}
	catch (string exception)
	{
		logger::Write(exception,logger::level::exception);
		throw exception;
	}
}

void communication::SendUDP(string text)
{
	if (text.length() > 65535) throw "Too long packets";   

	unsigned short dlugosc_stringa = text.length();  // short - 16 bit
	unsigned char * text_to_send = (unsigned char*)malloc(text.length());
				  

	memcpy(text_to_send, text.c_str(), text.length());

	sendto(UDP_socket,reinterpret_cast<const char*>(text_to_send),dlugosc_stringa,0,(SOCKADDR*)&UDP_addr,sizeof(SOCKADDR_IN));
	
	char temp_tab[2];
	logger::Write("Sending text UDP: "+text,logger::level::info);
	ostringstream ss;
	ss<<"Sending text UDP: ";

	for(int i=0;i<dlugosc_stringa;i++)
	{
		IntToHex((unsigned char)text_to_send[i], temp_tab);
		ss<<temp_tab[0] << temp_tab[1]<<" ";
	}
	logger::Write(ss.str(),logger::level::info);
	free(text_to_send);
}

string communication::ReceiveUDP()
{
	char buf[7000];
	int server_length=sizeof(UDP_addr);
	int n=recvfrom(UDP_socket,buf,6500,0,(SOCKADDR*)&UDP_addr,&server_length);
	
	/*if (n == SOCKET_ERROR)
	{
		ostringstream ss;
		ss << WSAGetLastError();
		logger::Write("Reciving error UDP: "+ss.str(),logger::level::fatal_error);
	}*/
	if(n>0)
	{	
		string text(buf, n);
		logger::Write("Reciving text UDP: "+text,logger::level::info);

		ostringstream ss;
		ss<<"Reciving text UDP: ";
		for(int i=0;i<text.length();i++)
		{
			ss<<hex<<(int)((unsigned char)text[i])<<" ";
		}
		logger::Write(ss.str(),logger::level::info);
		return text;
	}

	return "";
}

string communication::GetSHA1(string text)
{
	unsigned char hash[20];
	char hexstring[41];
	sha1::calc(text.c_str(),text.length(),hash);
	sha1::toHexString(hash, hexstring);
	string result=string(hexstring, strlen(hexstring));
	return result;
}



vector<string> communication::split(string text,char separator)
{
	vector<string> result;
	string temp="";
	int length=0;

	for(int i=0;i<=text.length();i++)
	{
		if(text[i]==separator || i==text.length())
		{
			result.push_back(temp);
			temp="";
		}
		else
		{
			temp=temp+text[i];
		}
	}
	return result;
}

void communication::SendReady()
{
	//hashlib.sha1(password_gracza + challenge2).hexdigest()
	//string sha=GetSHA1(password+resources::getInstance().game_info.challenge);
	string sha=GetSHA1(GetSHA1(ToLowerCase(login)+password)+resources::getInstance().game_info.challenge);
	SendUDP(sha);
	SendUDP(sha);
	SendUDP(sha);
	//SendTCP(sha);
}

int communication::HexToInt(char a,char b)
{
	//a*255+b (256)
	int a2=(int)a;
	int b2=(int)b;
	return a2*255+b2;	
}
void communication::IntToHex(unsigned char byte, char * hex)
{
	// musi byc unsigned char bo inaczej >> przesuwa w logice U2
	char lut[16] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};
	hex[0] = lut[byte >> 4];
	hex[1] = lut[byte & 15];
}