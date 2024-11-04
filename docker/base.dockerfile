FROM csegarragonz/dotfiles:0.2.0 AS dotfiles
FROM ubuntu:22.04

# ---------------------------
# Work. Env. Set-Up (do this first to benefit from caching)
# ---------------------------

# APT dependencies
RUN apt update \
    && apt upgrade -y \
    && apt install -y \
        clang \
        curl \
        libclang-dev \
        libdevmapper-dev \
        git

# Clone the dotfiles repo
RUN rm -rf ~/git/csegarragonz/dotfiles \
    && mkdir -p ~/git/csegarragonz/dotfiles \
    && git clone https://github.com/csegarragonz/dotfiles ~/git/csegarragonz/dotfiles

# Configure Neovim
COPY --from=dotfiles /neovim/build/bin/nvim /usr/bin/nvim
COPY --from=dotfiles /usr/local/share/nvim /usr/local/share/nvim
RUN curl -fLo ~/.local/share/nvim/site/autoload/plug.vim --create-dirs \
        https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim \
    && mkdir -p ~/.config/nvim/ \
    && ln -sf ~/git/csegarragonz/dotfiles/nvim/init.vim ~/.config/nvim/init.vim \
    && ln -sf ~/git/csegarragonz/dotfiles/nvim/after ~/.config/nvim/ \
    && ln -sf ~/git/csegarragonz/dotfiles/nvim/syntax ~/.config/nvim/ \
    && nvim +PlugInstall +qa \
    && nvim +PlugUpdate +qa

# Configure Bash
RUN ln -sf ~/git/csegarragonz/dotfiles/bash/.bashrc ~/.bashrc \
    && ln -sf ~/git/csegarragonz/dotfiles/bash/.bash_profile ~/.bash_profile \
    && ln -sf ~/git/csegarragonz/dotfiles/bash/.bash_aliases ~/.bash_aliases