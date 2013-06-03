using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Diagnostics;
using System.Web.Script.Serialization;
using Newtonsoft.Json.Linq;
using System.IO;

namespace NinjaTower_launcher
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();

            StreamReader rdr = new StreamReader("version.dat");
            string version=rdr.ReadLine();
            rdr.Close();

            this.Text = "NinjaTowerLauncher.exe (Build: " + Convert.ToString(File.GetLastWriteTimeUtc(Application.ExecutablePath)) + " UTC) | NinjaTower.exe (Build: " + Convert.ToString(File.GetLastWriteTimeUtc(Directory.GetCurrentDirectory() + "\\data\\NinjaTower.exe")) + " UTC) | version: "+version;
        }

        private void linkLabel1_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
        {
            Process.Start("http://ninjatower.eu/forum/index.php?action=register");
        }

        private void button1_Click(object sender, EventArgs e)
        {
            pictureBox1.Visible = false;
            button1.Visible = false;
            Data.Instance.login = textBox1.Text;
            Data.Instance.password = textBox2.Text;
            TCP.Instance.send_login(textBox1.Text,textBox2.Text);
        }

        int stan = 0;
        //stan 0 ->nie w kolejce
        //stan 1 ->w kolejce
        //stan 2 ->w wyborze postaci
        //stan 3 ->w grze
        //stan 4 ->wynik gry
        //stan 5 ->rekonekt

        private void stan0(string msgJSON) //stan 0 ->nie w kolejce
        {
            JObject jsonObj = JObject.Parse(msgJSON);
            string status = (string)(jsonObj["status"]);
            var form2 = Data.Instance.form2;

            if (status == "ok" && stan == 0)
            {
                stan = 1;
                form2.label3.Invoke(new Action(() => { form2.label3.Text = "Finding team please wait..."; }));
            }
            if (status == "fail" && stan == 0)
            {
                    stan = 0;
                    MessageBox.Show((string)(jsonObj["code"]),"Error");
                    form2.button1.Invoke(new Action(() => { form2.button1.Visible = true; }));

                    form2.button2.Invoke(new Action(() => { form2.button2.Visible= false; }));

                    form2.label3.Invoke(new Action(() => { form2.label3.Text = ""; }));

                    form2.pictureBox1.Invoke(new Action(() => { form2.pictureBox1.Visible = false; }));
           }

           if (status == "request_to_reconnect")
           {
              stan = 3;
              Data.Instance.IP = (string)(jsonObj["target_ip"]);
              Data.Instance.TCP = (string)(jsonObj["target_port_tcp"]);
              Data.Instance.UDP = (string)(jsonObj["target_port_udp"]);
              form2.Invoke(new Action(() => 
               {
                   form2.Visible = false;
                   Data.Instance.form4 = new Form4();
                   Data.Instance.form4.Show();
                   Data.Instance.form4.BringToFront();
               }));
           }
        }

        private void stan1(string msgJSON)//stan 1 ->w kolejce
        {
            JObject jsonObj = JObject.Parse(msgJSON);
            string status = (string)(jsonObj["status"]);
            var form2 = Data.Instance.form2;

            if (status == "ok" && stan == 1)
            {
                stan = 0;
                form2.button1.Invoke(new Action(() => { form2.button1.Visible = true; }));

                form2.button2.Invoke(new Action(() => { form2.button2.Visible= false; }));

                form2.label3.Invoke(new Action(() => { form2.label3.Text = ""; }));

                form2.pictureBox1.Invoke(new Action(() => { form2.pictureBox1.Visible = false; }));
            }

            if (status == "match_found" && stan == 1)
            {
                stan = 2;
                Data.Instance.team1 = (JArray) jsonObj["team1"];
                Data.Instance.team2 = (JArray)jsonObj["team2"];
                Data.Instance.heroes = (JArray)jsonObj["heroes"];

                for (int i = 0; i < Data.Instance.team2.Count; i++)
                {
                    if ((string)Data.Instance.team2[i] == Data.Instance.login)
                    {
                        JArray temp = Data.Instance.team1;
                        Data.Instance.team1 = Data.Instance.team2;
                        Data.Instance.team2 = temp;
                        break;
                    }
                }

                form2.Invoke(new Action(() => { form2.Visible = false; }));

                form2.Invoke(new Action(() => { Data.Instance.form3 = new Form3(); Data.Instance.form3.Show(); }));
                    
            }

        }

        private void stan2(string msgJSON)//stan 2 ->w wyborze postaci
        {

            JObject jsonObj = JObject.Parse(msgJSON);
            string status = (string)(jsonObj["status"]);
            var form2 = Data.Instance.form2;
            var form3 = Data.Instance.form3;

            if (status == "dodge_victim" && stan ==2)
            {
                stan = 1;
                MessageBox.Show("Somebody leave.\nReturning to the queue","Info");
                form2.Invoke(new Action(() => { form3.Dispose(); form2.BringToFront(); form2.Visible = true; }));
            }

            if (status == "hero_picked" && stan == 2)
            {
                string login=(string)(jsonObj["login"]);
                string hero = (string)(jsonObj["hero"]);

                for (int i = 0; i < Data.Instance.team1.Count; i++)
                {   
                    if ((string)Data.Instance.team1[i] == login)
                    {
                        form3.Invoke(new Action(() => 
                        { 
                            form3.team1[i].Load("data\\data\\heroes\\" + hero + "\\portarit.bmp");
                            form3.team1[i].Image = form3.DrawRamka(form3.team1[i].Image);
                        }));
                    }
                }

                for (int i = 0; i < Data.Instance.team2.Count; i++)
                {
                    if ((string)Data.Instance.team2[i] == login)
                    {
                        form3.Invoke(new Action(() => 
                        { 
                            form3.team2[i].Load("data\\data\\heroes\\" + hero + "\\portarit.bmp");
                            form3.team2[i].Image = form3.DrawRamka(form3.team2[i].Image);
                        }));
                    }
                }
            }

            if (status == "ok" && stan == 2)
            {
                form3.Invoke(new Action(() => 
                { 
                    form3.stan++;
                    if (form3.stan == 1) form3.button1.Visible = true;
                    if(form3.button1.Visible==true)form3.label2.Text = "";

                    for (int i = 0; i < form3.choice_hero.Count; i++)
                    {

                        if (form3.choice_hero[i].Name == form3.wybor_postaci)
                        {
                            form3.choice_hero[i].Load("data\\data\\heroes\\" + form3.choice_hero[i].Name + "\\portarit.bmp");
                            form3.choice_hero[i].Image = form3.DrawRamka(form3.choice_hero[i].Image);
                        }
                        else
                        {
                            form3.choice_hero[i].Load("data\\data\\heroes\\" + form3.choice_hero[i].Name + "\\portarit.bmp");
                            Bitmap b = new Bitmap(form3.choice_hero[i].Image);
                            b = form3.ImageToSepia(b);
                            form3.choice_hero[i].Image = b;
                            form3.choice_hero[i].Image = form3.DrawRamka(form3.choice_hero[i].Image);
                        }
                    }

                }));
            }

            if (status == "fail" && stan == 2)
            {
                MessageBox.Show((string)(jsonObj["code"]));
                form3.Invoke(new Action(() => { form3.label2.Text = "Selection hero failed"; }));
            }

            if (status == "hero_locked_in" && stan == 2)
            {
                string login = (string)(jsonObj["login"]);

                for (int i = 0; i < Data.Instance.team1.Count; i++)
                {
                    if ((string)Data.Instance.team1[i] == login)
                    {
                        form3.Invoke(new Action(() => 
                        { 
                            //form3.l_team1[i].ForeColor = Color.Green; 
                            form3.team1_anim[i].Visible = true;
                        }));
                    }
                }

                for (int i = 0; i < Data.Instance.team2.Count; i++)
                {
                    if ((string)Data.Instance.team2[i] == login)
                    {
                        form3.Invoke(new Action(() => 
                        { 
                            //form3.l_team2[i].ForeColor = Color.Green;
                            form3.team2_anim[i].Visible = true;
                        }));
                    }
                }

                if (login == Data.Instance.login)
                {
                    form3.Invoke(new Action(() =>
                    {
                        for (int i = 0; i < form3.choice_hero.Count; i++)
                        {
                            if (form3.choice_hero[i].Name == form3.wybor_postaci)
                            {
                                form3.pick = new PictureBox();
                                form3.pick.Left = form3.choice_hero[i].Location.X - 2;
                                form3.pick.Top = form3.choice_hero[i].Location.Y - 2;
                                form3.pick.Parent = form3.panel3;
                                form3.pick.Image = global::NinjaTower_launcher.Properties.Resources.pick_anim;
                                form3.pick.SizeMode = PictureBoxSizeMode.AutoSize;
                                form3.pick.Visible = true;
                                break;
                            }
                        }
                    }));
                }

            }

            if (status == "match_starting" && stan == 2)
            {
                string condition = (string)(jsonObj["condition"]);
                if (condition == "ok")
                {
                    stan=3;

                    Data.Instance.IP = (string)(jsonObj["target_ip"]);
                    Data.Instance.TCP = (string)(jsonObj["target_port_tcp"]);
                    Data.Instance.UDP = (string)(jsonObj["target_port_udp"]);
                    Data.Instance.start_main_game();

                    form2.Invoke(new Action(() => 
                    {
                        form2.label3.Text = "";
                        form2.button1.Visible = true;
                        form2.button2.Visible = false;
                        form2.pictureBox1.Visible = false;

                        form3.Dispose();
                        Data.Instance.form4 = new Form4();
                        Data.Instance.form4.Show();
                        Data.Instance.form4.BringToFront();
                    }));

                    
                    
                }

                if (condition == "fail")
                {
                    string msg= (string)(jsonObj["code"]);
                    MessageBox.Show(msg,"Error");
                    stan = 0;
                    form2.Invoke(new Action(() => 
                    { 
                        form3.Dispose();
                        form2.BringToFront();
                        form2.Show();                       
                        form2.label3.Text = "";
                        form2.button1.Visible = true;
                        form2.button2.Visible = false;
                        form2.pictureBox1.Visible = false;
                    }));

                }
            }

        }

        private void stan3(string msgJSON)//stan 3 ->w grze
        {
            JObject jsonObj = JObject.Parse(msgJSON);
            string status = (string)(jsonObj["status"]);
            var form2 = Data.Instance.form2;

            if (status == "round_ended") // bedzie trzeba to poprawic w przyszlosci :p
            {
                stan = 0;
                form2.Invoke(new Action(() =>
                {
                    form2.button1.Visible = true;
                    form2.button2.Visible = false;
                    form2.pictureBox1.Visible = false;
                    form2.label3.Text = "";
                    Data.Instance.form4.Dispose();
                    form2.Show();
                    form2.BringToFront();

                }));
            }
        }

        List<Label> etykiety=new List<Label>();
        List<Label> opis = new List<Label>();
        bool pierwszy_raz_staty = true;
        private void server_statistics(string msgJSON)
        {
            JObject jsonObj = JObject.Parse(msgJSON);
            string status = (string)(jsonObj["status"]);
            if (status == "server_statistics")
            {
                string online = (string)(jsonObj["players_online"]);
                JObject players_in_queue = (JObject)jsonObj["players_in_queue"];

                for (int i = 0; i < etykiety.Count; i++)
                {
                    Data.Instance.form2.Invoke(new Action(() =>
                    {
                        etykiety[i].Dispose();
                    }));
                }

                for (int i = 0; i < opis.Count; i++)
                {
                    Data.Instance.form2.Invoke(new Action(() =>
                    {
                      opis[i].Dispose();
                      }));
                }
                        
                etykiety.Clear();
                opis.Clear();
                int y = 0;        
                Data.Instance.form2.Invoke(new Action(() =>
                {
                    Font f = new Font("Arial", (float)17.0, FontStyle.Regular);
                    Label temp2 = new Label();
                    temp2.ForeColor = Color.FromArgb(40,30,24);
                    temp2.Left = 0;
                    temp2.Top = y ;
                    temp2.Parent = Data.Instance.form2.panel1;
                    temp2.AutoSize = true;
                    temp2.Font = f;
                    temp2.Text = "Players online:";
                    etykiety.Add(temp2);
                }));

                Data.Instance.form2.Invoke(new Action(() =>
                {
                    Font f = new Font("Arial", (float)17.0, FontStyle.Bold);
                    Label temp2 = new Label();
                    temp2.ForeColor = Color.FromArgb(40, 30, 24);
                    temp2.Left = 280;
                    temp2.Top = y;
                    temp2.Parent = Data.Instance.form2.panel1;
                    temp2.AutoSize = true;
                    temp2.Font = f;
                    temp2.Text = online;
                    opis.Add(temp2);
                }));

                y += 30;

                foreach ( JToken token in players_in_queue.Children())
                {
                    string name=((JProperty)token).Name.ToString();
                    string value = (string)token.First;

                    if (pierwszy_raz_staty == true)
                    {
                        Data.Instance.form2.Invoke(new Action(() =>
                        {
                            Data.Instance.form2.listBox1.Items.Add(name);
                        }));
                    }
                    Data.Instance.form2.Invoke(new Action(() =>
                    {
                        Font f = new Font("Arial", (float)17.0, FontStyle.Regular);
                        Label temp2 = new Label();
                        temp2.ForeColor = Color.FromArgb(40, 30, 24);
                        temp2.Left = 0;
                        temp2.Top = y;
                        temp2.Parent = Data.Instance.form2.panel1;
                        temp2.AutoSize = true;
                        temp2.Font = f;
                        temp2.Text = "In queue " + name + ":";
                        etykiety.Add(temp2);
                    }));

                    Data.Instance.form2.Invoke(new Action(() =>
                    {
                        Font f = new Font("Arial", (float)17.0, FontStyle.Bold);
                        Label temp2 = new Label();
                        temp2.ForeColor = Color.FromArgb(40, 30, 24);
                        temp2.Left = 280;
                        temp2.Top = y;
                        temp2.Parent = Data.Instance.form2.panel1;
                        temp2.AutoSize = true;
                        temp2.Font = f;
                        temp2.Text = value;
                        opis.Add(temp2);
                    }));

                    y += 30;
                }
                if (pierwszy_raz_staty == true)
                {
                    Data.Instance.form2.Invoke(new Action(() =>
                    {
                        Data.Instance.form2.listBox1.SelectedIndex = 0;
                    }));
                    pierwszy_raz_staty = false;
                }


            }
        }


        private void backgroundWorkerTCP_DoWork(object sender, DoWorkEventArgs e)
        {
            while (true)
            {
                string msgJSON=TCP.Instance.recieve();
                if (msgJSON != "")
                {
                    switch(stan)
                    {
                        case 0: stan0(msgJSON); break;
                        case 1: stan1(msgJSON); break;
                        case 2: stan2(msgJSON); break;
                        case 3: stan3(msgJSON); break;
                    }

                    server_statistics(msgJSON);
                }
            }
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            TCP.Instance.connect();
            timer1.Enabled = true;
        }

        private void Form1_FormClosed(object sender, FormClosedEventArgs e)
        {
            Environment.Exit(0);
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            TCP.Instance.ping();
        }

        private void Form1_Shown(object sender, EventArgs e)
        {
            this.Activate();
            this.Focus();
            this.BringToFront();
        }

        private void textBox2_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (e.KeyChar == (char)13)
            {
                button1_Click(this, null);
            }
 
        }

 
    }
}
