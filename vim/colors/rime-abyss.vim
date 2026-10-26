" Rime Abyss: The coldest take, on a darker background: no yellow or orange anywhere, with rose as the only warm accent.
" https://github.com/w0x7y/rime
set background=dark
hi clear
if exists('syntax_on')
  syntax reset
endif
let g:colors_name = 'rime-abyss'

hi Normal guifg=#c2cde0 ctermfg=252 guibg=#15171c ctermbg=234 gui=NONE cterm=NONE
hi NormalFloat guifg=#c2cde0 ctermfg=252 guibg=#1d2026 ctermbg=234 gui=NONE cterm=NONE
hi Cursor guifg=#15171c ctermfg=234 guibg=#c2cde0 ctermbg=252 gui=NONE cterm=NONE
hi! link lCursor Cursor
hi! link CursorIM Cursor
hi CursorLine guibg=#1d2026 ctermbg=234 gui=NONE cterm=NONE
hi CursorColumn guibg=#1d2026 ctermbg=234 gui=NONE cterm=NONE
hi ColorColumn guibg=#191c21 ctermbg=234 gui=NONE cterm=NONE
hi CursorLineNr guifg=#dde5f2 ctermfg=254 gui=bold cterm=bold
hi LineNr guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi SignColumn guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi FoldColumn guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi Folded guifg=#9aa4b6 ctermfg=248 guibg=#1d2026 ctermbg=234 gui=NONE cterm=NONE
hi VertSplit guifg=#252830 ctermfg=235 gui=NONE cterm=NONE
hi StatusLine guifg=#9aa4b6 ctermfg=248 guibg=#1d2026 ctermbg=234 gui=NONE cterm=NONE
hi StatusLineNC guifg=#6b768c ctermfg=66 guibg=#1d2026 ctermbg=234 gui=NONE cterm=NONE
hi! link StatusLineTerm StatusLine
hi! link StatusLineTermNC StatusLineNC
hi TabLine guifg=#6b768c ctermfg=66 guibg=#1d2026 ctermbg=234 gui=NONE cterm=NONE
hi TabLineSel guifg=#dde5f2 ctermfg=254 guibg=#15171c ctermbg=234 gui=bold cterm=bold
hi TabLineFill guibg=#111317 ctermbg=233 gui=NONE cterm=NONE
hi ToolbarLine guibg=#1d2026 ctermbg=234 gui=NONE cterm=NONE
hi ToolbarButton guifg=#dde5f2 ctermfg=254 guibg=#2c3039 ctermbg=236 gui=bold cterm=bold
hi Pmenu guifg=#c2cde0 ctermfg=252 guibg=#1d2026 ctermbg=234 gui=NONE cterm=NONE
hi PmenuSel guibg=#2c3039 ctermbg=236 gui=bold cterm=bold
hi PmenuSbar guibg=#1d2026 ctermbg=234 gui=NONE cterm=NONE
hi PmenuThumb guibg=#6b768c ctermbg=66 gui=NONE cterm=NONE
hi PmenuMatch guifg=#6b9cf4 ctermfg=75 gui=bold cterm=bold
hi PmenuMatchSel guifg=#6b9cf4 ctermfg=75 guibg=#2c3039 ctermbg=236 gui=bold cterm=bold
hi PmenuKind guifg=#937ff2 ctermfg=105 gui=NONE cterm=NONE
hi PmenuKindSel guifg=#937ff2 ctermfg=105 guibg=#2c3039 ctermbg=236 gui=NONE cterm=NONE
hi PmenuExtra guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi PmenuExtraSel guifg=#9aa4b6 ctermfg=248 guibg=#2c3039 ctermbg=236 gui=NONE cterm=NONE
hi! link WildMenu PmenuSel
hi Visual guibg=#2c3039 ctermbg=236 gui=NONE cterm=NONE
hi! link VisualNOS Visual
hi Search guifg=#dde5f2 ctermfg=254 guibg=#3b5452 ctermbg=239 gui=NONE cterm=NONE
hi CurSearch guifg=#15171c ctermfg=234 guibg=#9cf0dc ctermbg=158 gui=bold cterm=bold
hi! link IncSearch CurSearch
hi MatchParen guifg=#dde5f2 ctermfg=254 guibg=#2c3039 ctermbg=236 gui=bold cterm=bold
hi NonText guifg=#444b5a ctermfg=239 gui=NONE cterm=NONE
hi EndOfBuffer guifg=#2c3039 ctermfg=236 gui=NONE cterm=NONE
hi SpecialKey guifg=#444b5a ctermfg=239 gui=NONE cterm=NONE
hi Conceal guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi Directory guifg=#6b9cf4 ctermfg=75 gui=NONE cterm=NONE
hi Title guifg=#6b9cf4 ctermfg=75 gui=bold cterm=bold
hi Question guifg=#6fd0a8 ctermfg=79 gui=NONE cterm=NONE
hi MoreMsg guifg=#6fd0a8 ctermfg=79 gui=NONE cterm=NONE
hi ModeMsg guifg=#c2cde0 ctermfg=252 gui=bold cterm=bold
hi ErrorMsg guifg=#e8879f ctermfg=175 gui=NONE cterm=NONE
hi WarningMsg guifg=#9cf0dc ctermfg=158 gui=NONE cterm=NONE
hi QuickFixLine guibg=#2c3039 ctermbg=236 gui=bold cterm=bold
hi SpellBad guisp=#e8879f gui=undercurl cterm=undercurl
hi SpellCap guisp=#9cf0dc gui=undercurl cterm=undercurl
hi SpellRare guisp=#937ff2 gui=undercurl cterm=undercurl
hi SpellLocal guisp=#4fb4dc gui=undercurl cterm=undercurl
hi DiffAdd guibg=#233331 ctermbg=236 gui=NONE cterm=NONE
hi DiffChange guibg=#1f2736 ctermbg=235 gui=NONE cterm=NONE
hi DiffDelete guifg=#e8879f ctermfg=175 guibg=#352830 ctermbg=236 gui=NONE cterm=NONE
hi DiffText guibg=#2f3f5d ctermbg=238 gui=NONE cterm=NONE
hi Added guifg=#6fd0a8 ctermfg=79 gui=NONE cterm=NONE
hi Changed guifg=#6b9cf4 ctermfg=75 gui=NONE cterm=NONE
hi Removed guifg=#e8879f ctermfg=175 gui=NONE cterm=NONE
hi! link diffAdded Added
hi! link diffChanged Changed
hi! link diffRemoved Removed
hi diffFile guifg=#6b9cf4 ctermfg=75 gui=bold cterm=bold
hi diffLine guifg=#937ff2 ctermfg=105 gui=NONE cterm=NONE
hi diffIndexLine guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi Comment guifg=#6b768c ctermfg=66 gui=italic cterm=italic
hi Constant guifg=#d4aaff ctermfg=183 gui=NONE cterm=NONE
hi String guifg=#6fd0a8 ctermfg=79 gui=NONE cterm=NONE
hi Character guifg=#6fd0a8 ctermfg=79 gui=NONE cterm=NONE
hi Number guifg=#d4aaff ctermfg=183 gui=NONE cterm=NONE
hi Boolean guifg=#d4aaff ctermfg=183 gui=NONE cterm=NONE
hi Float guifg=#d4aaff ctermfg=183 gui=NONE cterm=NONE
hi Identifier guifg=#c2cde0 ctermfg=252 gui=NONE cterm=NONE
hi Function guifg=#6b9cf4 ctermfg=75 gui=NONE cterm=NONE
hi Statement guifg=#937ff2 ctermfg=105 gui=NONE cterm=NONE
hi Conditional guifg=#e8879f ctermfg=175 gui=bold cterm=bold
hi Repeat guifg=#9cf0dc ctermfg=158 gui=NONE cterm=NONE
hi Label guifg=#9cf0dc ctermfg=158 gui=NONE cterm=NONE
hi Operator guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi Keyword guifg=#937ff2 ctermfg=105 gui=NONE cterm=NONE
hi Exception guifg=#e8879f ctermfg=175 gui=NONE cterm=NONE
hi PreProc guifg=#9cf0dc ctermfg=158 gui=NONE cterm=NONE
hi Include guifg=#937ff2 ctermfg=105 gui=NONE cterm=NONE
hi Define guifg=#937ff2 ctermfg=105 gui=NONE cterm=NONE
hi Macro guifg=#4fb4dc ctermfg=74 gui=NONE cterm=NONE
hi PreCondit guifg=#9cf0dc ctermfg=158 gui=NONE cterm=NONE
hi Type guifg=#9cf0dc ctermfg=158 gui=NONE cterm=NONE
hi StorageClass guifg=#937ff2 ctermfg=105 gui=NONE cterm=NONE
hi Structure guifg=#9cf0dc ctermfg=158 gui=NONE cterm=NONE
hi Typedef guifg=#9cf0dc ctermfg=158 gui=NONE cterm=NONE
hi Special guifg=#4fb4dc ctermfg=74 gui=NONE cterm=NONE
hi SpecialChar guifg=#4fb4dc ctermfg=74 gui=NONE cterm=NONE
hi Tag guifg=#e8879f ctermfg=175 gui=NONE cterm=NONE
hi Delimiter guifg=#7182a8 ctermfg=67 gui=NONE cterm=NONE
hi SpecialComment guifg=#9aa4b6 ctermfg=248 gui=italic cterm=italic
hi Debug guifg=#e8879f ctermfg=175 gui=NONE cterm=NONE
hi Underlined gui=underline cterm=underline
hi Ignore guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi Error guifg=#e8879f ctermfg=175 gui=NONE cterm=NONE
hi Todo guifg=#15171c ctermfg=234 guibg=#9cf0dc ctermbg=158 gui=bold cterm=bold

let g:terminal_ansi_colors = ['#2c3039', '#e8879f', '#6fd0a8', '#9cf0dc', '#6b9cf4', '#937ff2', '#4fb4dc', '#c2cde0', '#6b768c', '#eda1b4', '#8fdabb', '#b2f3e4', '#8cb2f6', '#ab9bf5', '#76c5e4', '#f2f6fc']
