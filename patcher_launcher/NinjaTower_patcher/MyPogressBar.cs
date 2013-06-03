using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;

namespace NinjaTower_patcher
{
    class MyPogressBar: ProgressBar
    {
        Bitmap b1 = new Bitmap(global::NinjaTower_patcher.Properties.Resources.back);

        public override Image BackgroundImage
        {
            get
            {
                return base.BackgroundImage;
            }
            set
            {
                base.BackgroundImage = value;
                this.Size = base.BackgroundImage.Size;
                this.Refresh();
            }
        }

        public MyPogressBar()
        {
            this.SetStyle(ControlStyles.AllPaintingInWmPaint, true);
            this.SetStyle(ControlStyles.UserPaint, true);
            this.BackgroundImage = b1;
        }

        protected override void OnPaintBackground(PaintEventArgs e)
        {
            // None... Helps control the flicker.   
        }

        protected override void OnPaint(PaintEventArgs e)
        {

           const int inset = 0; // A single inset value to control teh sizing of the inner rect.

            using (Image offscreenImage = new Bitmap(this.Width, this.Height))
            {
                using (Graphics offscreen = Graphics.FromImage(offscreenImage))
                {
                    Rectangle rect = new Rectangle(0, 0, this.Width, this.Height);

                    rect.Inflate(new Size(-inset, -inset)); // Deflate inner rect.
                    rect.Width = (int)(rect.Width * ((double)this.Value / this.Maximum));
                    if (rect.Width == 0) rect.Width = 1; // Can't draw rec with width of 0.

                    Color c1 = System.Drawing.Color.FromArgb(((int)(((byte)(245)))), ((int)(((byte)(250)))), ((int)(((byte)(90))))); 
                    Color c2 = System.Drawing.Color.FromArgb(((int)(((byte)(21)))), ((int)(((byte)(40)))), ((int)(((byte)(8)))));
                    LinearGradientBrush brush = new LinearGradientBrush(rect, c1, c2, LinearGradientMode.Vertical);
                    offscreen.DrawImage(this.BackgroundImage, 0, 0);
                    offscreen.FillRectangle(brush, inset, inset, rect.Width, rect.Height);
                    
                    e.Graphics.DrawImage(offscreenImage, 0, 0);
                    offscreenImage.Dispose();
                }

            }
            
        }
    }
}
