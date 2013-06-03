using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Collections.Specialized;
using System.Net;

namespace NinjaTower_launcher
{
    public partial class Form5 : Form
    {
        public Form5()
        {
            InitializeComponent();
        }

        private static class Http
        {
            public static byte[] Post(string uri, NameValueCollection pairs)
            {
                byte[] response = null;
                using (WebClient client = new WebClient())
                {
                    response = client.UploadValues(uri, pairs);
                }
                return response;
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (textBox1.Text != "" && textBox2.Text != "" && comboBox1.Text != "")
            {
                string subject = textBox1.Text;
                string category = comboBox1.Text;
                string message = textBox2.Text;
                string login = Data.Instance.login;

                Http.Post("http://ninjatower.eu/mail_feedback.php", new NameValueCollection() {
                { "login", login },
                { "subject", subject },
                { "category", category },
                { "message", message }
                });

                this.DialogResult = DialogResult.OK;
            }
            else
            {
                MessageBox.Show("Please fill all fields");
            }
        }
    }
}
