using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Drawing.Imaging;

namespace NinjaTower_launcher
{
    public partial class Form3 : Form
    {
        public List<PictureBox> choice_hero, team1, team2,team1_anim,team2_anim;
        public List<Label> l_team1, l_team2;
        public PictureBox pick;
        int time = 60;
        public Form3()
        {
            InitializeComponent();

            choice_hero = new List<PictureBox>();
            team1 = new List<PictureBox>();
            team2 = new List<PictureBox>();
            l_team1 = new List<Label>();
            l_team2 = new List<Label>();
            team1_anim = new List<PictureBox>();
            team2_anim = new List<PictureBox>();

            for (int i = 0; i < Data.Instance.team1.Count; i++)
            {
                Font f = new Font("Arial", (float)19.0, FontStyle.Bold);
                Label temp2 = new Label();
                temp2.ForeColor = Color.Black;
                temp2.Left = 70;
                temp2.Top = 15 + i * 60;
                temp2.Parent = panel1;
                temp2.Height = 40;
                temp2.Width = 500;
                temp2.Font = f;

                temp2.Text = (string)Data.Instance.team1[i];
                temp2.Visible = true;
                l_team1.Add(temp2);

                PictureBox temp = new PictureBox();
                temp.Left = 10;
                temp.Top = 15 + i * 60;
                temp.Parent = panel1;
                temp.SizeMode = PictureBoxSizeMode.AutoSize;
                temp.Visible = true;
                team1.Add(temp);

                PictureBox temp3 = new PictureBox();
                temp3.Left = 8;
                temp3.Top = 13 + i * 60;
                temp3.Parent = panel1;
                temp3.Image=global::NinjaTower_launcher.Properties.Resources.pick_anim;
                temp3.SizeMode = PictureBoxSizeMode.AutoSize;
                temp3.Visible = false;
                team1_anim.Add(temp3);


            }

            for (int i = 0; i < Data.Instance.team2.Count; i++)
            {
                Font f = new Font("Arial", (float)19.0, FontStyle.Bold);
                Label temp2 = new Label();
                temp2.ForeColor = Color.Black;
                temp2.Left = 70;
                temp2.Top = 15 + i * 60;
                temp2.Parent = panel2;
                temp2.Height = 40;
                temp2.Width = 500;
                temp2.Font = f;

                temp2.Text = (string)Data.Instance.team2[i];
                temp2.Visible = true;
                l_team2.Add(temp2);

                PictureBox temp = new PictureBox();
                temp.Left = 10;
                temp.Top = 15 + i * 60;
                temp.Parent = panel2;
                temp.SizeMode = PictureBoxSizeMode.AutoSize;
                temp.Visible = true;
                team2.Add(temp);

                PictureBox temp3 = new PictureBox();
                temp3.Left = 8;
                temp3.Top = 13 + i * 60;
                temp3.Parent = panel2;
                temp3.Image = global::NinjaTower_launcher.Properties.Resources.pick_anim;
                temp3.SizeMode = PictureBoxSizeMode.AutoSize;
                temp3.Visible = false;
                team2_anim.Add(temp3);
            }

            for (int i = 0; i < Data.Instance.heroes.Count; i++)
            {
                PictureBox temp = new PictureBox();
                temp.Left = 15 + i * 60;
                temp.Top = 15;
                temp.Parent = panel3;
                temp.SizeMode = PictureBoxSizeMode.AutoSize;

                temp.Load("data\\data\\heroes\\" + Data.Instance.heroes[i] + "\\portarit.bmp");
                Bitmap b = new Bitmap(temp.Image);
                b=ImageToSepia(b);
                temp.Image = b;
                temp.Image = DrawRamka(temp.Image);

                temp.Name = (string)Data.Instance.heroes[i];
                temp.Click += this.pictureBox_Click;
                temp.Cursor = Cursors.Hand;
                temp.Visible = true;
                choice_hero.Add(temp);
            }
            label3.Text = "Game start in " + Convert.ToString(time) + " seconds";
        }

        private void Form3_FormClosed(object sender, FormClosedEventArgs e)
        {
            Application.Exit();
        }

        public int stan = 0;
        bool locked = false;
        
        public string wybor_postaci = "";

        private void pictureBox_Click(object sender, EventArgs e)
        {
            if (locked==false)
            {
                PictureBox oPictureBox = (PictureBox)sender;
                wybor_postaci = oPictureBox.Name;
                string text = "{\"operation\" : \"match_pick\",\"hero\" : \"" + oPictureBox.Name + "\"}";

                TCP.Instance.send(text);
                label2.Text = "Trying select - " + oPictureBox.Name + ". Please wait...";
            }

        }

        private void button1_Click(object sender, EventArgs e)
        {
            button1.Visible= false;
            label2.Text = "Picked hero. Waiting for others...";
            locked = true;
            string text = "{\"operation\" : \"hero_lock_in\"}";
            TCP.Instance.send(text);

        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            time--;
            label3.Text = "Game start in " + Convert.ToString(time) + " seconds";
            if (time == 0)
            {
                button1.Enabled = false;
                locked = true;
                stan++;
                timer1.Enabled = false;
            }

        }

        private void Form3_Shown(object sender, EventArgs e)
        {
            this.Activate();
            this.Focus();
            this.BringToFront();
        }

        public Bitmap ImageToSepia(Bitmap bmp)
        {
            Rectangle rect = new Rectangle(0, 0, bmp.Width, bmp.Height);
            BitmapData bmpData = bmp.LockBits(rect, ImageLockMode.ReadWrite, PixelFormat.Format32bppRgb);
            IntPtr ptr = bmpData.Scan0;

            int numPixels = bmpData.Width * bmp.Height;
            int numBytes = numPixels * 4;
            byte[] rgbValues = new byte[numBytes];

            System.Runtime.InteropServices.Marshal.Copy(ptr, rgbValues, 0, numBytes);
            for (int i = 0; i < rgbValues.Length; i += 4)
            {
                int inputRed = rgbValues[i + 2];
                int inputGreen = rgbValues[i + 1];
                int inputBlue = rgbValues[i + 0];

                rgbValues[i + 2] = (byte)Math.Min(255, (int)((.393 * inputRed) + (.769 * inputGreen) + (.189 * inputBlue))); //red
                rgbValues[i + 1] = (byte)Math.Min(255, (int)((.349 * inputRed) + (.686 * inputGreen) + (.168 * inputBlue))); //green
                rgbValues[i + 0] = (byte)Math.Min(255, (int)((.272 * inputRed) + (.534 * inputGreen) + (.131 * inputBlue))); //blue
            }

            System.Runtime.InteropServices.Marshal.Copy(rgbValues, 0, ptr, numBytes);
            bmp.UnlockBits(bmpData);

            return bmp;
        }

        public Image DrawRamka(Image img)
        {
            Graphics g = Graphics.FromImage(img);
            Pen p=new Pen(Color.FromArgb(61,53,40));
            g.DrawRectangle(p, 0, 0, img.Width-1, img.Height-1);
            return img;
        }

    }
}
