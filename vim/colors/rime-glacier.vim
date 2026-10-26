" Rime Glacier: Crisper accents with clear separation between every syntax role, on a lighter background.
" https://github.com/w0x7y/rime
set background=dark
hi clear
if exists('syntax_on')
  syntax reset
endif
let g:colors_name = 'rime-glacier'

hi Normal guifg=#c5cedd ctermfg=252 guibg=#2a2f37 ctermbg=236 gui=NONE cterm=NONE
hi NormalFloat guifg=#c5cedd ctermfg=252 guibg=#323841 ctermbg=237 gui=NONE cterm=NONE
hi Cursor guifg=#2a2f37 ctermfg=236 guibg=#c5cedd ctermbg=252 gui=NONE cterm=NONE
hi! link lCursor Cursor
hi! link CursorIM Cursor
hi CursorLine guibg=#323841 ctermbg=237 gui=NONE cterm=NONE
hi CursorColumn guibg=#323841 ctermbg=237 gui=NONE cterm=NONE
hi ColorColumn guibg=#2e343c ctermbg=236 gui=NONE cterm=NONE
hi CursorLineNr guifg=#dfe5ee ctermfg=254 gui=bold cterm=bold
hi LineNr guifg=#737e94 ctermfg=244 gui=NONE cterm=NONE
hi SignColumn guifg=#737e94 ctermfg=244 gui=NONE cterm=NONE
hi FoldColumn guifg=#737e94 ctermfg=244 gui=NONE cterm=NONE
hi Folded guifg=#9aa4b6 ctermfg=248 guibg=#323841 ctermbg=237 gui=NONE cterm=NONE
hi VertSplit guifg=#3a404b ctermfg=238 gui=NONE cterm=NONE
hi StatusLine guifg=#9aa4b6 ctermfg=248 guibg=#323841 ctermbg=237 gui=NONE cterm=NONE
hi StatusLineNC guifg=#737e94 ctermfg=244 guibg=#323841 ctermbg=237 gui=NONE cterm=NONE
hi! link StatusLineTerm StatusLine
hi! link StatusLineTermNC StatusLineNC
hi TabLine guifg=#737e94 ctermfg=244 guibg=#323841 ctermbg=237 gui=NONE cterm=NONE
hi TabLineSel guifg=#dfe5ee ctermfg=254 guibg=#2a2f37 ctermbg=236 gui=bold cterm=bold
hi TabLineFill guibg=#22272d ctermbg=235 gui=NONE cterm=NONE
hi ToolbarLine guibg=#323841 ctermbg=237 gui=NONE cterm=NONE
hi ToolbarButton guifg=#dfe5ee ctermfg=254 guibg=#414854 ctermbg=239 gui=bold cterm=bold
hi Pmenu guifg=#c5cedd ctermfg=252 guibg=#323841 ctermbg=237 gui=NONE cterm=NONE
hi PmenuSel guibg=#414854 ctermbg=239 gui=bold cterm=bold
hi PmenuSbar guibg=#323841 ctermbg=237 gui=NONE cterm=NONE
hi PmenuThumb guibg=#737e94 ctermbg=244 gui=NONE cterm=NONE
hi PmenuMatch guifg=#6eaaf0 ctermfg=75 gui=bold cterm=bold
hi PmenuMatchSel guifg=#6eaaf0 ctermfg=75 guibg=#414854 ctermbg=239 gui=bold cterm=bold
hi PmenuKind guifg=#ae94f0 ctermfg=141 gui=NONE cterm=NONE
hi PmenuKindSel guifg=#ae94f0 ctermfg=141 guibg=#414854 ctermbg=239 gui=NONE cterm=NONE
hi PmenuExtra guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi PmenuExtraSel guifg=#9aa4b6 ctermfg=248 guibg=#414854 ctermbg=239 gui=NONE cterm=NONE
hi! link WildMenu PmenuSel
hi Visual guibg=#414854 ctermbg=239 gui=NONE cterm=NONE
hi! link VisualNOS Visual
hi Search guifg=#dfe5ee ctermfg=254 guibg=#5e5f54 ctermbg=240 gui=NONE cterm=NONE
hi CurSearch guifg=#2a2f37 ctermfg=236 guibg=#e3dc9e ctermbg=187 gui=bold cterm=bold
hi! link IncSearch CurSearch
hi MatchParen guifg=#dfe5ee ctermfg=254 guibg=#414854 ctermbg=239 gui=bold cterm=bold
hi NonText guifg=#525a6a ctermfg=59 gui=NONE cterm=NONE
hi EndOfBuffer guifg=#414854 ctermfg=239 gui=NONE cterm=NONE
hi SpecialKey guifg=#525a6a ctermfg=59 gui=NONE cterm=NONE
hi Conceal guifg=#737e94 ctermfg=244 gui=NONE cterm=NONE
hi Directory guifg=#6eaaf0 ctermfg=75 gui=NONE cterm=NONE
hi Title guifg=#6eaaf0 ctermfg=75 gui=bold cterm=bold
hi Question guifg=#88d8a0 ctermfg=115 gui=NONE cterm=NONE
hi MoreMsg guifg=#88d8a0 ctermfg=115 gui=NONE cterm=NONE
hi ModeMsg guifg=#c5cedd ctermfg=252 gui=bold cterm=bold
hi ErrorMsg guifg=#e07a90 ctermfg=174 gui=NONE cterm=NONE
hi WarningMsg guifg=#e3dc9e ctermfg=187 gui=NONE cterm=NONE
hi QuickFixLine guibg=#414854 ctermbg=239 gui=bold cterm=bold
hi SpellBad guisp=#e07a90 gui=undercurl cterm=undercurl
hi SpellCap guisp=#e3dc9e gui=undercurl cterm=undercurl
hi SpellRare guisp=#ae94f0 gui=undercurl cterm=undercurl
hi SpellLocal guisp=#6fd0d8 gui=undercurl cterm=undercurl
hi DiffAdd guibg=#384847 ctermbg=238 gui=NONE cterm=NONE
hi DiffChange guibg=#323e4d ctermbg=237 gui=NONE cterm=NONE
hi DiffDelete guifg=#e07a90 ctermfg=174 guibg=#453a44 ctermbg=238 gui=NONE cterm=NONE
hi DiffText guibg=#3e546f ctermbg=240 gui=NONE cterm=NONE
hi Added guifg=#88d8a0 ctermfg=115 gui=NONE cterm=NONE
hi Changed guifg=#6eaaf0 ctermfg=75 gui=NONE cterm=NONE
hi Removed guifg=#e07a90 ctermfg=174 gui=NONE cterm=NONE
hi! link diffAdded Added
hi! link diffChanged Changed
hi! link diffRemoved Removed
hi diffFile guifg=#6eaaf0 ctermfg=75 gui=bold cterm=bold
hi diffLine guifg=#ae94f0 ctermfg=141 gui=NONE cterm=NONE
hi diffIndexLine guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi Comment guifg=#737e94 ctermfg=244 gui=italic cterm=italic
hi Constant guifg=#f2a7e0 ctermfg=218 gui=NONE cterm=NONE
hi String guifg=#88d8a0 ctermfg=115 gui=NONE cterm=NONE
hi Character guifg=#88d8a0 ctermfg=115 gui=NONE cterm=NONE
hi Number guifg=#f2a7e0 ctermfg=218 gui=NONE cterm=NONE
hi Boolean guifg=#f2a7e0 ctermfg=218 gui=NONE cterm=NONE
hi Float guifg=#f2a7e0 ctermfg=218 gui=NONE cterm=NONE
hi Identifier guifg=#c5cedd ctermfg=252 gui=NONE cterm=NONE
hi Function guifg=#6eaaf0 ctermfg=75 gui=NONE cterm=NONE
hi Statement guifg=#ae94f0 ctermfg=141 gui=NONE cterm=NONE
hi Conditional guifg=#e07a90 ctermfg=174 gui=bold cterm=bold
hi Repeat guifg=#e3dc9e ctermfg=187 gui=NONE cterm=NONE
hi Label guifg=#e3dc9e ctermfg=187 gui=NONE cterm=NONE
hi Operator guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi Keyword guifg=#ae94f0 ctermfg=141 gui=NONE cterm=NONE
hi Exception guifg=#e07a90 ctermfg=174 gui=NONE cterm=NONE
hi PreProc guifg=#e3dc9e ctermfg=187 gui=NONE cterm=NONE
hi Include guifg=#ae94f0 ctermfg=141 gui=NONE cterm=NONE
hi Define guifg=#ae94f0 ctermfg=141 gui=NONE cterm=NONE
hi Macro guifg=#6fd0d8 ctermfg=80 gui=NONE cterm=NONE
hi PreCondit guifg=#e3dc9e ctermfg=187 gui=NONE cterm=NONE
hi Type guifg=#e3dc9e ctermfg=187 gui=NONE cterm=NONE
hi StorageClass guifg=#ae94f0 ctermfg=141 gui=NONE cterm=NONE
hi Structure guifg=#e3dc9e ctermfg=187 gui=NONE cterm=NONE
hi Typedef guifg=#e3dc9e ctermfg=187 gui=NONE cterm=NONE
hi Special guifg=#6fd0d8 ctermfg=80 gui=NONE cterm=NONE
hi SpecialChar guifg=#6fd0d8 ctermfg=80 gui=NONE cterm=NONE
hi Tag guifg=#e07a90 ctermfg=174 gui=NONE cterm=NONE
hi Delimiter guifg=#788bb0 ctermfg=103 gui=NONE cterm=NONE
hi SpecialComment guifg=#9aa4b6 ctermfg=248 gui=italic cterm=italic
hi Debug guifg=#e07a90 ctermfg=174 gui=NONE cterm=NONE
hi Underlined gui=underline cterm=underline
hi Ignore guifg=#737e94 ctermfg=244 gui=NONE cterm=NONE
hi Error guifg=#e07a90 ctermfg=174 gui=NONE cterm=NONE
hi Todo guifg=#2a2f37 ctermfg=236 guibg=#e3dc9e ctermbg=187 gui=bold cterm=bold

let g:terminal_ansi_colors = ['#414854', '#e07a90', '#88d8a0', '#e3dc9e', '#6eaaf0', '#ae94f0', '#6fd0d8', '#c5cedd', '#737e94', '#e797a8', '#a2e1b5', '#e9e4b3', '#8ebdf3', '#c0acf3', '#8fdae1', '#f3f6fa']
