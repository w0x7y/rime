" Rime: Soft and muted pastels for long sessions.
" https://github.com/w0x7y/rime
set background=dark
hi clear
if exists('syntax_on')
  syntax reset
endif
let g:colors_name = 'rime'

hi Normal guifg=#c3ccd9 ctermfg=252 guibg=#23272e ctermbg=235 gui=NONE cterm=NONE
hi NormalFloat guifg=#c3ccd9 ctermfg=252 guibg=#2b3038 ctermbg=236 gui=NONE cterm=NONE
hi Cursor guifg=#23272e ctermfg=235 guibg=#c3ccd9 ctermbg=252 gui=NONE cterm=NONE
hi! link lCursor Cursor
hi! link CursorIM Cursor
hi CursorLine guibg=#2b3038 ctermbg=236 gui=NONE cterm=NONE
hi CursorColumn guibg=#2b3038 ctermbg=236 gui=NONE cterm=NONE
hi ColorColumn guibg=#272c33 ctermbg=236 gui=NONE cterm=NONE
hi CursorLineNr guifg=#dce2eb ctermfg=254 gui=bold cterm=bold
hi LineNr guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi SignColumn guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi FoldColumn guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi Folded guifg=#9aa4b6 ctermfg=248 guibg=#2b3038 ctermbg=236 gui=NONE cterm=NONE
hi VertSplit guifg=#333842 ctermfg=237 gui=NONE cterm=NONE
hi StatusLine guifg=#9aa4b6 ctermfg=248 guibg=#2b3038 ctermbg=236 gui=NONE cterm=NONE
hi StatusLineNC guifg=#6b768c ctermfg=66 guibg=#2b3038 ctermbg=236 gui=NONE cterm=NONE
hi! link StatusLineTerm StatusLine
hi! link StatusLineTermNC StatusLineNC
hi TabLine guifg=#6b768c ctermfg=66 guibg=#2b3038 ctermbg=236 gui=NONE cterm=NONE
hi TabLineSel guifg=#dce2eb ctermfg=254 guibg=#23272e ctermbg=235 gui=bold cterm=bold
hi TabLineFill guibg=#1d2026 ctermbg=234 gui=NONE cterm=NONE
hi ToolbarLine guibg=#2b3038 ctermbg=236 gui=NONE cterm=NONE
hi ToolbarButton guifg=#dce2eb ctermfg=254 guibg=#3a404b ctermbg=238 gui=bold cterm=bold
hi Pmenu guifg=#c3ccd9 ctermfg=252 guibg=#2b3038 ctermbg=236 gui=NONE cterm=NONE
hi PmenuSel guibg=#3a404b ctermbg=238 gui=bold cterm=bold
hi PmenuSbar guibg=#2b3038 ctermbg=236 gui=NONE cterm=NONE
hi PmenuThumb guibg=#6b768c ctermbg=66 gui=NONE cterm=NONE
hi PmenuMatch guifg=#7aa4e4 ctermfg=110 gui=bold cterm=bold
hi PmenuMatchSel guifg=#7aa4e4 ctermfg=110 guibg=#3a404b ctermbg=238 gui=bold cterm=bold
hi PmenuKind guifg=#bb98d6 ctermfg=140 gui=NONE cterm=NONE
hi PmenuKindSel guifg=#bb98d6 ctermfg=140 guibg=#3a404b ctermbg=238 gui=NONE cterm=NONE
hi PmenuExtra guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi PmenuExtraSel guifg=#9aa4b6 ctermfg=248 guibg=#3a404b ctermbg=238 gui=NONE cterm=NONE
hi! link WildMenu PmenuSel
hi Visual guibg=#3a404b ctermbg=238 gui=NONE cterm=NONE
hi! link VisualNOS Visual
hi Search guifg=#dce2eb ctermfg=254 guibg=#59564c ctermbg=240 gui=NONE cterm=NONE
hi CurSearch guifg=#23272e ctermfg=235 guibg=#e4d098 ctermbg=186 gui=bold cterm=bold
hi! link IncSearch CurSearch
hi MatchParen guifg=#dce2eb ctermfg=254 guibg=#3a404b ctermbg=238 gui=bold cterm=bold
hi NonText guifg=#4b5262 ctermfg=240 gui=NONE cterm=NONE
hi EndOfBuffer guifg=#3a404b ctermfg=238 gui=NONE cterm=NONE
hi SpecialKey guifg=#4b5262 ctermfg=240 gui=NONE cterm=NONE
hi Conceal guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi Directory guifg=#7aa4e4 ctermfg=110 gui=NONE cterm=NONE
hi Title guifg=#7aa4e4 ctermfg=110 gui=bold cterm=bold
hi Question guifg=#9ad8ac ctermfg=115 gui=NONE cterm=NONE
hi MoreMsg guifg=#9ad8ac ctermfg=115 gui=NONE cterm=NONE
hi ModeMsg guifg=#c3ccd9 ctermfg=252 gui=bold cterm=bold
hi ErrorMsg guifg=#d98a9c ctermfg=175 gui=NONE cterm=NONE
hi WarningMsg guifg=#e4d098 ctermfg=186 gui=NONE cterm=NONE
hi QuickFixLine guibg=#3a404b ctermbg=238 gui=bold cterm=bold
hi SpellBad guisp=#d98a9c gui=undercurl cterm=undercurl
hi SpellCap guisp=#e4d098 gui=undercurl cterm=undercurl
hi SpellRare guisp=#bb98d6 gui=undercurl cterm=undercurl
hi SpellLocal guisp=#7cc4d0 gui=undercurl cterm=undercurl
hi DiffAdd guibg=#354241 ctermbg=237 gui=NONE cterm=NONE
hi DiffChange guibg=#2d3644 ctermbg=237 gui=NONE cterm=NONE
hi DiffDelete guifg=#d98a9c ctermfg=175 guibg=#3e363f ctermbg=237 gui=NONE cterm=NONE
hi DiffText guibg=#3d4d65 ctermbg=239 gui=NONE cterm=NONE
hi Added guifg=#9ad8ac ctermfg=115 gui=NONE cterm=NONE
hi Changed guifg=#7aa4e4 ctermfg=110 gui=NONE cterm=NONE
hi Removed guifg=#d98a9c ctermfg=175 gui=NONE cterm=NONE
hi! link diffAdded Added
hi! link diffChanged Changed
hi! link diffRemoved Removed
hi diffFile guifg=#7aa4e4 ctermfg=110 gui=bold cterm=bold
hi diffLine guifg=#bb98d6 ctermfg=140 gui=NONE cterm=NONE
hi diffIndexLine guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi Comment guifg=#6b768c ctermfg=66 gui=italic cterm=italic
hi Constant guifg=#e8a8cc ctermfg=182 gui=NONE cterm=NONE
hi String guifg=#9ad8ac ctermfg=115 gui=NONE cterm=NONE
hi Character guifg=#9ad8ac ctermfg=115 gui=NONE cterm=NONE
hi Number guifg=#e8a8cc ctermfg=182 gui=NONE cterm=NONE
hi Boolean guifg=#e8a8cc ctermfg=182 gui=NONE cterm=NONE
hi Float guifg=#e8a8cc ctermfg=182 gui=NONE cterm=NONE
hi Identifier guifg=#c3ccd9 ctermfg=252 gui=NONE cterm=NONE
hi Function guifg=#7aa4e4 ctermfg=110 gui=NONE cterm=NONE
hi Statement guifg=#bb98d6 ctermfg=140 gui=NONE cterm=NONE
hi Conditional guifg=#d98a9c ctermfg=175 gui=bold cterm=bold
hi Repeat guifg=#e4d098 ctermfg=186 gui=NONE cterm=NONE
hi Label guifg=#e4d098 ctermfg=186 gui=NONE cterm=NONE
hi Operator guifg=#9aa4b6 ctermfg=248 gui=NONE cterm=NONE
hi Keyword guifg=#bb98d6 ctermfg=140 gui=NONE cterm=NONE
hi Exception guifg=#d98a9c ctermfg=175 gui=NONE cterm=NONE
hi PreProc guifg=#e4d098 ctermfg=186 gui=NONE cterm=NONE
hi Include guifg=#bb98d6 ctermfg=140 gui=NONE cterm=NONE
hi Define guifg=#bb98d6 ctermfg=140 gui=NONE cterm=NONE
hi Macro guifg=#7cc4d0 ctermfg=116 gui=NONE cterm=NONE
hi PreCondit guifg=#e4d098 ctermfg=186 gui=NONE cterm=NONE
hi Type guifg=#e4d098 ctermfg=186 gui=NONE cterm=NONE
hi StorageClass guifg=#bb98d6 ctermfg=140 gui=NONE cterm=NONE
hi Structure guifg=#e4d098 ctermfg=186 gui=NONE cterm=NONE
hi Typedef guifg=#e4d098 ctermfg=186 gui=NONE cterm=NONE
hi Special guifg=#7cc4d0 ctermfg=116 gui=NONE cterm=NONE
hi SpecialChar guifg=#7cc4d0 ctermfg=116 gui=NONE cterm=NONE
hi Tag guifg=#d98a9c ctermfg=175 gui=NONE cterm=NONE
hi Delimiter guifg=#7987a1 ctermfg=103 gui=NONE cterm=NONE
hi SpecialComment guifg=#9aa4b6 ctermfg=248 gui=italic cterm=italic
hi Debug guifg=#d98a9c ctermfg=175 gui=NONE cterm=NONE
hi Underlined gui=underline cterm=underline
hi Ignore guifg=#6b768c ctermfg=66 gui=NONE cterm=NONE
hi Error guifg=#d98a9c ctermfg=175 gui=NONE cterm=NONE
hi Todo guifg=#23272e ctermfg=235 guibg=#e4d098 ctermbg=186 gui=bold cterm=bold

let g:terminal_ansi_colors = ['#3a404b', '#d98a9c', '#9ad8ac', '#e4d098', '#7aa4e4', '#bb98d6', '#7cc4d0', '#c3ccd9', '#6b768c', '#e1a4b2', '#b0e1be', '#eadaaf', '#97b8ea', '#caafdf', '#99d1da', '#f0f3f8']
