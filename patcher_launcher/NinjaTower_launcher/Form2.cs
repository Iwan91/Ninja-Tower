using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace NinjaTower_launcher
{
    public partial class Form2 : Form
    {
        public Form2()
        {
            InitializeComponent();
            Show();
        }

        private void Form2_FormClosed(object sender, FormClosedEventArgs e)
        {
            Environment.Exit(0);
        }


        private void button1_Click(object sender, EventArgs e)
        {
            button1.Visible= false;
            button2.Visible = true;
            pictureBox1.Visible = true;
            label3.Text = "Sending request to server";
            string text = "{\"operation\" : \"enqueue\",\"gametype\" : \"" + listBox1.SelectedItem + "\"}";
            TCP.Instance.send(text);

        }

        private void button2_Click(object sender, EventArgs e)
        {
            label3.Text = "Trying cancel";
            string text = "{\"operation\" : \"dequeue\"}";
            TCP.Instance.send(text);
        }

        private void button3_Click(object sender, EventArgs e)
        {
            string msg = "";
            msg+="Core members:\n\n";

            msg+="Piotr \"Henrietta\" Maślanka - server-side programmer.\n";
            msg+="Email: piotr.maslanka@henrietta.com.pl\n\n";

            msg+="Kamil \"Iwan91\" Iwiński - client-side programmer.\n";
            msg+="Email: kamil3453@yahoo.com\n\n";

            msg+="Mateusz \"Globock\" Sieradziński - spriter.\n"; 
            msg+="Email: pppglobock@gmail.com\n\n";

            msg += "Piotr Maszlanka - hero editor and map editor programmer.\n";
            msg += "Email: p.maszlanka@wp.pl\n\n";

            msg+="Special thanks for:\n\n";

            msg += "Michał Żak - GUI design.\n";
            msg+="Email: turimaren@gmail.com";

            MessageBox.Show(msg, "Credits");
        }

        private void Form2_Shown(object sender, EventArgs e)
        {
            this.Activate();
            this.Focus();
            this.BringToFront();
        }

        private void listBox1_DrawItem(object sender, DrawItemEventArgs e)
        {
            Image image = new Bitmap(listBox1.Size.Width, listBox1.Size.Height);
            Graphics image2= Graphics.FromImage(image);

            Bitmap b= global::NinjaTower_launcher.Properties.Resources.ListBox_bg;
            Rectangle r=new Rectangle(0,0,listBox1.Size.Width,listBox1.Size.Height);
            image2.DrawImageUnscaledAndClipped(b, r);

            Color c1 = System.Drawing.Color.FromArgb(((int)(((byte)(56)))), ((int)(((byte)(22)))), ((int)(((byte)(5)))));
            Color c2 = System.Drawing.Color.FromArgb(((int)(((byte)(221)))), ((int)(((byte)(216)))), ((int)(((byte)(216)))));
            Brush reportsForegroundBrush = new SolidBrush(c1); 
            Brush reportsForegroundBrushSelected = new SolidBrush(c2);

            listBox1.ItemHeight = 32;

            for (int i = 0; i < listBox1.Items.Count;i++)
            {
                String text = listBox1.Items[i].ToString();
                image2.DrawString(text, e.Font, reportsForegroundBrush,listBox1.GetItemRectangle(i).Location);
            }

            int index = listBox1.SelectedIndex;

            if (index >= 0 && index < listBox1.Items.Count)
            {
                String text2 = listBox1.Items[index].ToString();

               // Color color = (selected) ? Color.FromKnownColor(KnownColor.Highlight) : (((index % 2) == 0) ? Color.White : Color.Gray);
               // e.Graphics.FillRectangle(new SolidBrush(color), e.Bounds);

                // Print text
                image2.DrawString(text2, e.Font, reportsForegroundBrushSelected, listBox1.GetItemRectangle(index).Location);
            }

            e.Graphics.DrawImage(image, 0, 0);

        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            TCP.Instance.send_server_statistics();
        }

        private void button4_Click(object sender, EventArgs e)
        {
            Form5 form5 = new Form5();
            form5.ShowDialog();
            form5.Dispose();      
        }







    }
}
