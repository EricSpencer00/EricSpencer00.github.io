---
title: "My ~/.zshrc file"
date: 2025-03-20T00:00:00Z
draft: false
description: "Ran every time I open a terminal"
image: "/previews/zshrc.png"
tags: ["zshrc", "terminal", "bash"]
---

Ran every time that I open a terminal on my Macbook Pro.

```sh
PROMPT='%F{green}$USER%f $ '
echo "8b    d8  dP\"Yb   88888 88 
88b  d88 dP   Yb     88 88 
88YbdP88 Yb   dP o.  88 88 
88 YY 88  YbodP  \"bod8\" 88 \n"

# Customized shell prompt in PS1
export PS1="%F{28}$USER%F{reset} %# "

# Ruby Gems PATH
export PATH="/usr/local/lib/ruby/gems/3.3.0/bin:$PATH"

# Configure GPG for terminal
export GPG_TTY=$(tty)

# Android SDK and platform-tools PATH configuration
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin:$PATH"

# Java environment configuration
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
export PATH="$JAVA_HOME/bin:$PATH"

# Combine Android SDK and Java paths into a single line
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools:$JAVA_HOME/bin:$PATH"

# Useful aliases for common commands
alias gs='git status'
alias gp='git pull --rebase'
alias ..='cd ..'
alias c='clear'
alias ls='ls --color=auto'
alias gpt='cd ~/Documents/Github/Project && source venv/bin/activate && python3 gpt.py'
alias py='python3 -m venv venv'
alias v='source venv/bin/activate'

# Color settings for 'ls' command
export LSCOLORS="GxFxCxDxBxegedabagaced"

# Google Cloud SDK PATH
export PATH="$PATH:$HOME/google-cloud-sdk/bin"

# Include additional paths for npm global binaries
export PATH="$HOME/.npm-global/bin:$PATH"

# Python SSL Certificate
export SSL_CERT_FILE=$(python -m certifi)
export PATH=$HOME/.npm-global/bin:$PATH
```

Notes: 

* gpt.py is a CLI for ChatGPT. You can install it via [TerminalGPT](https://github.com/EricSpencer00/TerminalGPT)
* You should use --rebase with git pull

