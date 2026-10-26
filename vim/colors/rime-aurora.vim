" Rime Aurora: Vivid neon accents on a darker background.
" https://github.com/w0x7y/rime
set background=dark
hi clear
if exists('syntax_on')
  syntax reset
endif
let g:colors_name = 'rime-aurora'

hi Normal guifg=#c8d2e2 ctermfg=188 guibg=#1c1f25 ctermbg=234 gui=NONE cterm=NONE
hi NormalFloat guifg=#c8d2e2 ctermfg=188 guibg=#24282f ctermbg=235 gui=NONE cterm=NONE
hi Cursor guifg=#1c1f25 ctermfg=234 guibg=#c8d2e2 ctermbg=188 gui=NONE cterm=NONE
hi! link lCursor Cursor
hi! link CursorIM Cursor
hi CursorLine guibg=#24282f ctermbg=235 gui=NONE cterm=NONE
hi CursorColumn guibg=#24282f ctermbg=235 gui=NONE cterm=NONE
hi ColorColumn guibg=#20242a ctermbg=235 gui=NONE cterm=NONE
hi CursorLineNr guifg=#e0e7f2 ctermfg=254 gui=bold cterm=bold
hi LineNr guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi SignColumn guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi FoldColumn guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi Folded guifg=#9aa4b6 ctermfg=248 guibg=#24282f ctermbg=235 gui=NONE cterm=NONE
hi VertSplit guifg=#2c3039 ctermfg=236 gui=NONE cterm=NONE
hi StatusLine guifg=#9aa4b6 ctermfg=248 guibg=#24282f ctermbg=235 gui=NONE cterm=NONE
hi StatusLineNC guifg=#6b768c ctermfg=66 guibg=#24282f ctermbg=235 gui=NONE cterm=NONE
hi! link StatusLineTerm StatusLine
hi! link StatusLineTermNC StatusLineNC
hi TabLine guifg=#6b768c ctermfg=66 guibg=#24282f ctermbg=235 gui=NONE cterm=NONE
hi TabLineSel guifg=#e0e7f2 ctermfg=254 guibg=#1c1f25 ctermbg=234 gui=bold cterm=bold
hi TabLineFill guibg=#17191e ctermbg=234 gui=NONE cterm=NONE
hi ToolbarLine guibg=#24282f ctermbg=235 gui=NONE cterm=NONE
hi ToolbarButton guifg=#e0e7f2 ctermfg=254 guibg=#333842 ctermbg=237 gui=bold cterm=bold
hi Pmenu guifg=#c8d2e2 ctermfg=188 guibg=#24282f ctermbg=235 gui=NONE cterm=NONE
hi PmenuSel guibg=#333842 ctermbg=237 gui=bold cterm=bold
hi PmenuSbar guibg=#24282f ctermbg=235 gui=NONE cterm=NONE
hi PmenuThumb guibg=#6b768c ctermbg=66 gui=NONE cterm=NONE
hi PmenuMatch guifg=#4fa2ff ctermfg=75 gui=bold cterm=bold
hi PmenuMatchSel guifg=#4fa2ff ctermfg=75 guibg=#333842 ctermbg=237 gui=bold cterm=bold
hi PmenuKind guifg=#9b7dff ctermfg=105 gui=NONE cterm=NONE
hi PmenuKindSel guifg=#9b7dff ctermfg=105 guibg=#333842 ctermbg=237 gui=NONE cterm=NONE
hi PmenuExtra guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi PmenuExtraSel guifg=#9aa4b6 ctermfg=248 guibg=#333842 ctermbg=237 gui=NONE cterm=NONE
hi! link WildMenu PmenuSel
hi Visual guibg=#333842 ctermbg=237 gui=NONE cterm=NONE
hi! link VisualNOS Visual
hi Search guifg=#e0e7f2 ctermfg=254 guibg=#555a3d ctermbg=239 gui=NONE cterm=NONE
hi CurSearch guifg=#1c1f25 ctermfg=234 guibg=#e6f07c ctermbg=192 gui=bold cterm=bold
hi! link IncSearch CurSearch
hi MatchParen guifg=#e0e7f2 ctermfg=254 guibg=#333842 ctermbg=237 gui=bold cterm=bold
hi NonText guifg=#474f5e ctermfg=239 gui=NONE cterm=NONE
hi EndOfBuffer guifg=#333842 ctermfg=237 gui=NONE cterm=NONE
hi SpecialKey guifg=#474f5e ctermfg=239 gui=NONE cterm=NONE
hi Conceal guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi Directory guifg=#4fa2ff ctermfg=75 gui=NONE cterm=NONE
hi Title guifg=#4fa2ff ctermfg=75 gui=bold cterm=bold
hi Question guifg=#5ef0a6 ctermfg=85 gui=NONE cterm=NONE
hi MoreMsg guifg=#5ef0a6 ctermfg=85 gui=NONE cterm=NONE
hi ModeMsg guifg=#c8d2e2 ctermfg=188 gui=bold cterm=bold
hi ErrorMsg guifg=#ff6f91 ctermfg=204 gui=NONE cterm=NONE
hi WarningMsg guifg=#e6f07c ctermfg=192 gui=NONE cterm=NONE
hi QuickFixLine guibg=#333842 ctermbg=237 gui=bold cterm=bold
hi SpellBad guisp=#ff6f91 gui=undercurl cterm=undercurl
hi SpellCap guisp=#e6f07c gui=undercurl cterm=undercurl
hi SpellRare guisp=#9b7dff gui=undercurl cterm=undercurl
hi SpellLocal guisp=#38dce8 gui=undercurl cterm=undercurl
hi DiffAdd guibg=#263e38 ctermbg=236 gui=NONE cterm=NONE
hi DiffChange guibg=#222f3f ctermbg=236 gui=NONE cterm=NONE
hi DiffDelete guifg=#ff6f91 ctermfg=204 guibg=#3e2b35 ctermbg=236 gui=NONE cterm=NONE
hi DiffText guibg=#2b4666 ctermbg=238 gui=NONE cterm=NONE
hi Added guifg=#5ef0a6 ctermfg=85 gui=NONE cterm=NONE
hi Changed guifg=#4fa2ff ctermfg=75 gui=NONE cterm=NONE
hi Removed guifg=#ff6f91 ctermfg=204 gui=NONE cterm=NONE
hi! link diffAdded Added
hi! link diffChanged Changed
hi! link diffRemoved Removed
hi diffFile guifg=#4fa2ff ctermfg=75 gui=bold cterm=bold
hi diffLine guifg=#9b7dff ctermfg=105 gui=NONE cterm=NONE
hi diffIndexLine guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi Comment guifg=#6b768c ctermfg=66 gui=italic cterm=italic
hi Constant guifg=#ff8fe0 ctermfg=212 gui=NONE cterm=NONE
hi String guifg=#5ef0a6 ctermfg=85 gui=NONE cterm=NONE
hi Character guifg=#5ef0a6 ctermfg=85 gui=NONE cterm=NONE
hi Number guifg=#ff8fe0 ctermfg=212 gui=NONE cterm=NONE
hi Boolean guifg=#ff8fe0 ctermfg=212 gui=NONE cterm=NONE
hi Float guifg=#ff8fe0 ctermfg=212 gui=NONE cterm=NONE
hi Identifier guifg=#c8d2e2 ctermfg=188 gui=NONE cterm=NONE
hi Function guifg=#4fa2ff ctermfg=75 gui=NONE cterm=NONE
hi Statement guifg=#9b7dff ctermfg=105 gui=NONE cterm=NONE
hi Conditional guifg=#ff6f91 ctermfg=204 gui=bold cterm=bold
hi Repeat guifg=#e6f07c ctermfg=192 gui=NONE cterm=NONE
hi Label guifg=#e6f07c ctermfg=192 gui=NONE cterm=NONE
hi Operator guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi Keyword guifg=#9b7dff ctermfg=105 gui=NONE cterm=NONE
hi Exception guifg=#ff6f91 ctermfg=204 gui=NONE cterm=NONE
hi PreProc guifg=#e6f07c ctermfg=192 gui=NONE cterm=NONE
hi Include guifg=#9b7dff ctermfg=105 gui=NONE cterm=NONE
hi Define guifg=#9b7dff ctermfg=105 gui=NONE cterm=NONE
hi Macro guifg=#38dce8 ctermfg=80 gui=NONE cterm=NONE
hi PreCondit guifg=#e6f07c ctermfg=192 gui=NONE cterm=NONE
hi Type guifg=#e6f07c ctermfg=192 gui=NONE cterm=NONE
hi StorageClass guifg=#9b7dff ctermfg=105 gui=NONE cterm=NONE
hi Structure guifg=#e6f07c ctermfg=192 gui=NONE cterm=NONE
hi Typedef guifg=#e6f07c ctermfg=192 gui=NONE cterm=NONE
hi Special guifg=#38dce8 ctermfg=80 gui=NONE cterm=NONE
hi SpecialChar guifg=#38dce8 ctermfg=80 gui=NONE cterm=NONE
hi Tag guifg=#ff6f91 ctermfg=204 gui=NONE cterm=NONE
hi Delimiter guifg=#7084b7 ctermfg=67 gui=NONE cterm=NONE
hi SpecialComment guifg=#9aa4b6 ctermfg=248 gui=italic cterm=italic
hi Debug guifg=#ff6f91 ctermfg=204 gui=NONE cterm=NONE
hi Underlined gui=underline cterm=underline
hi Ignore guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi Error guifg=#ff6f91 ctermfg=204 gui=NONE cterm=NONE
hi Todo guifg=#1c1f25 ctermfg=234 guibg=#e6f07c ctermbg=192 gui=bold cterm=bold

let g:terminal_ansi_colors = ['#333842', '#ff6f91', '#5ef0a6', '#e6f07c', '#4fa2ff', '#9b7dff', '#38dce8', '#c8d2e2', '#6b768c', '#ff8fa9', '#81f3ba', '#ecf399', '#76b6ff', '#b19aff', '#64e4ed', '#f5f8fc']
