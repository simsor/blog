---
title: "Kindle hacking: jailbreaking your Kindle 4 and writing Kindlets"
date: 2020-12-27 22:10:12
draft: false
---

I have been back at my folks for winter holiday, which means I'm rediscovering some old stuff I had laying around. One of these is a [Kindle 4](https://en.wikipedia.org/wiki/Amazon_Kindle#Kindle_4), an old ebook reader which was gathering dust in the corner of my room.

After seeing someone use it as a weather station, I started to look up how I could go about running custom code on this thing. It turns out it's pretty easy to get SSH access to the device as `root`, and from there add custom applications, or even access the framebuffer directly.

Most information comes from the [MobileRead Wiki](https://wiki.mobileread.com/wiki/Main_Page), especially the page [Kindle4NTHacking](https://wiki.mobileread.com/wiki/Kindle4NTHacking).

## Rebooting into diagnostics mode and adding a developer key

Most code running on the Kindle has to be signed by a trusted developer key. This includes:

- Kindle firmware updates
- Kindle applets (called "Kindlets" by Amazon)

Usually, these two are the only ways to execute code. Thankfully, the Kindle 4 can be rebooted in "Diagnostics Mode", which allows us to run some simple scripts.

The [Kindle NT4 jailbreak](http://www.mobileread.com/forums/showthread.php?t=191158) will use this loophole to add a set of custom signing keys to the system keystore. This way, we will be able to run our own code!

Download the above ZIP file and extract `data.tar.gz` (which contains the custom keys, as well as a script to install them) and `ENABLE_DIAGS` to the root of your Kindle by plugging it to your PC. `ENABLE_DIAGS` will ask the Kindle to reboot into diagnostics mode on the next boot.

Eject your Kindle and reboot it. You should end up in a bizarre and new menu!

Then,

- Select "D) Exit, Reboot or Disable Diags" by using the arrow keys and pressing OK
- Select "Q) Reboot System", then press the left key on the d-pad to select the option.

Your Kindle will reboot, it may take some time, don't be afraid!

Once you have rebooted, you should see a new book added to your library: "You are Jailbroken".

## Installing USBNetwork & KUAL

The first hack we will install will enable us to access the Kindle using SSH over WiFi. Download `kindle-usbnetwork-0.57.N-k4.zip` from [this forum thread](https://www.mobileread.com/forums/showthread.php?t=88004). Extract `Update_usbnetwork_0.57.N_k4_install.bin` from the ZIP file and place it at the root of your Kindle.

Eject it and go to "Menu -> Settings -> Menu -> Update Kindle". This will reboot your Kindle and install the USBNetwork package. Because you installed custom developer keys in the previous step, your device will install this update without complaining! 

Once this is done, download [KUAL](https://www.mobileread.com/forums/showthread.php?t=203326) and extract the `azw2` file to the `documents/` folder on your Kindle. KUAL stands for Kindle Unified Application Launcher, and it will greatly improve your experience when using Kindle hacks!

Your should also install the [MobileRead Kindlet Kit](https://www.mobileread.com/forums/showthread.php?t=233932), which will install the required keys and prerequisites. Copy the `Update_mkk-20141129-k4-ALL_install.bin` file to your Kindle and install the update.

Once this is all done, you should be able to start KUAL from your Home menu and access the "USBNetwork" configuration menu! Go to "USBNetwork -> (Next page) -> Allow SSH over WiFi", then "USBNetwork -> Toggle USBNetwork". You can check whether this worked by running "USBNetwork status".

If USBNetwork is running correctly, point your SSH client at your Kindle's IP with the `root` account. The password can be computed using [this nifty website](https://www.sven.de/kindle/).

You can also add your SSH key to `kindle:/usbnetwork/etc/authorized_keys`.

Feel free to snoop around the filesystem, there's a bunch of really interesting stuff in there...

## Adding custom Kindlets

The [MobileRead forum](https://www.mobileread.com/forums/forumdisplay.php?f=150) is a goldmine when it comes to Kindle development. It seems to be pretty active too!

Kindlets are installed in `kindle:/documents/` and have the `azw2` extension. Using your SSH access, download the file `/opt/amazon/ebook/lib/Kindlet-1.3.jar` to your computer: this is the main KDK file (Kindlet Development Kit). I recommend you follow [this tutorial](http://cowlark.com/kindle/getting-started.html), which gives a great starting project if you want to write your own Kindlets.

Here are some things to keep in mind:

- You will need the [Oracle JDK 1.5](https://www.oracle.com/java/technologies/java-archive-javase5-downloads.html)
- The latest Ant release will refuse to compile for such an old version. I successfully used [Ant 1.9.15](https://archive.apache.org/dist/ant/binaries/).
- You don't need to generate your own signing keys. Just use the well known `dntest` keys, for example [from here](https://bitbucket.org/ixtab/ktfonthack/src/master/developer.keystore)

Here's an updated `build.xml` which also signs the JAR file and pushes it to your Kindle with SSH (there's a couple things to adapt to your context):

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<project basedir="." default="azw2" name="HelloWorld">

	<taskdef name="retroweaver" classname="net.sourceforge.retroweaver.ant.RetroWeaverTask">
		<classpath>
			<pathelement location="lib/retroweaver-all-2.0.7.jar" />
		</classpath>
	</taskdef>

	<property environment="env" />
	<property name="debuglevel" value="source,lines,vars" />
	<property name="target" value="1.5" />
	<property name="source" value="1.5" />

	<property name="keystorePath" value="developer.keystore" />
	<property name="keystorePass" value="password" />
	<property name="signName" value="test" />
	<property name="kindleIP" value="192.168.1.66" />

	<path id="app.classpath">
		<pathelement location="bin" />
		<pathelement location="../Kindlet-1.3.jar" />
	</path>

	<target name="init">
		<mkdir dir="bin" />
		<copy includeemptydirs="false" todir="bin">
			<fileset dir="src">
				<exclude name="**/*.launch" />
				<exclude name="**/*.java" />
			</fileset>
		</copy>
	</target>

	<target name="clean">
		<delete dir="bin" />
	</target>

	<target depends="clean" name="cleanall" />
	<target depends="build-subprojects,build-project" name="build" />

	<target name="weave" depends="build">
		<unzip src="lib/asm-3.1.jar" dest="bin" />
		<unzip src="lib/retroweaver-rt-2.0.7.jar" dest="bin" />
		<retroweaver srcdir="bin" />
	</target>

	<target name="jar" depends="weave">
		<jar destfile="${ant.project.name}.jar"
			manifest="${ant.project.name}.manifest">
			<fileset dir="bin"/>
			<fileset dir="." includes="res/**"/>
		</jar>
	</target>

	<target name="build-subprojects" />
	<target depends="init" name="build-project">
		<echo message="${ant.project.name}: ${ant.file}" />
		<javac debug="true" debuglevel="${debuglevel}" destdir="bin" source="${source}" target="${target}">
			<src path="src" />
			<classpath refid="app.classpath" />
		</javac>
	</target>

	<target name="sign" depends="jar">
		<signjar jar="${ant.project.name}.jar" alias="dn${signName}" storepass="${keystorePass}" keystore="${keystorePath}" />
		<signjar jar="${ant.project.name}.jar" alias="di${signName}" storepass="${keystorePass}" keystore="${keystorePath}"  />
		<signjar jar="${ant.project.name}.jar" alias="dk${signName}" storepass="${keystorePass}" keystore="${keystorePath}"  />
		<!--digestalg="SHA1" sigalg="SHA1withDSA"-->
	</target>

	<target name="azw2" depends="sign">
		<move file="${ant.project.name}.jar" tofile="${ant.project.name}.azw2" />
	</target>

	<target name="deploy" depends="azw2">
		<scp file="${ant.project.name}.azw2" todir="root@${kindleIP}:/mnt/us/documents/" password="fiona156" trust="true"/>
	</target>
</project>
```

Kindlets are developed using AWT, which is *ancient*. The custom JVM they are using also has a bunch of weird specificities, and seems very brittle. This is why the next blog post will explore advanced internals and how to directly write to the e-ink display with native code!

Stay tuned :)