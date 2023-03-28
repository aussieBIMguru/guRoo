# guRoo

# What is this?
guRoo is/will be a toolbar for the use with pyRevit built by Gavin Crump (aka Aussie BIM Guru). Having used and taught Dynamo for many years now, he's come to see pyRevit as a natural 'next step' for users looking to package up more efficient, stable and scalable tools to organisations.

# Who is it for?
These tools will generally be aimed towards architects looking to get more out of Revit and/or learn more about pyRevit. Expect tools to typically focus on efficiency gains usually made in the mid to late stages of project delivery (as well as some purely miscellaneous tools).

Read more at the wiki here: https://github.com/aussieBIMguru/guRoo/wiki

# Directly Installing guRoo
The following method can be used to avoid installing pyRevit via the Settings menu from within Revit itself, and might be beneficial to automate company related installation process' as well. Thanks to Jean-Marc Couffin for suggesting/helping write this section!

1. Install pyRevit from https://github.com/eirannejad/pyRevit/releases
2. WIN+R, then type 'cmd'
3. In the command line, install the extension with the following command pyrevit extend ui guRoo https://github.com/aussieBIMguru/guRoo.git --dest="C:\thePathWhereYouWantItInstalled" --branch=main
4. If Revit was opened, use the reload button of pyRevit

# Manually installing guRoo
If you want to quickly set up guRoo yourself, you can simply add it to your Roaming folder like below (reach this by typing %appdata% into the explorer address bar), and copy the contents of this git to that folder instead of using the CLI method above. For basic users this is generally the recommended approach:

![guRoo path](https://user-images.githubusercontent.com/58870499/228242863-d85d1583-4da9-40cb-b869-42231d4cee75.PNG)
