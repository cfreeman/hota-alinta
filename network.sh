#!/bin/bash

sudo apt install -y hostapd

sudo systemctl unmask hostapd
sudo systemctl enable hostapd

sudo apt install -y dnsmasq
sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent

echo -e "interface wlan0\n\tstatic ip_address=192.168.4.1/24\n\tnohook wpa_supplicant" | sudo tee -a /etc/dhcpcd.conf
echo -e "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.d/routed-ap.conf

sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo netfilter-persistent save

sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
echo -e "interface=wlan0\ndhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h\ndomain=wlan\naddress=/gw.wlan/192.168.4.1" | sudo tee -a /etc/dnsmasq.conf

sudo rfkill unblock wlan

echo -e "country_code=AU\ninterface=wlan0\nssid=sensor9\nhw_mode=g\nchannel=7\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nwpa=2\nwpa_passphrase=XXXX\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP" | sudo tee -a /etc/hostapd/hostapd.conf
sudo systemctl reboot