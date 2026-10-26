" Rime Frost: Frost-white paper under the same cold accents, deepened to read on it.
" https://github.com/w0x7y/rime
set background=light
hi clear
if exists('syntax_on')
  syntax reset
endif
let g:colors_name = 'rime-frost'

hi Normal guifg=#363d4a ctermfg=237 guibg=#eef1f5 ctermbg=255 gui=NONE cterm=NONE
hi NormalFloat guifg=#363d4a ctermfg=237 guibg=#e3e7ee ctermbg=254 gui=NONE cterm=NONE
hi Cursor guifg=#eef1f5 ctermfg=255 guibg=#363d4a ctermbg=237 gui=NONE cterm=NONE
hi! link lCursor Cursor
hi! link CursorIM Cursor
hi CursorLine guibg=#e3e7ee ctermbg=254 gui=NONE cterm=NONE
hi CursorColumn guibg=#e3e7ee ctermbg=254 gui=NONE cterm=NONE
hi ColorColumn guibg=#e9ecf2 ctermbg=255 gui=NONE cterm=NONE
hi CursorLineNr guifg=#272d37 ctermfg=236 gui=bold cterm=bold
hi LineNr guifg=#7f899b ctermfg=245 gui=NONE cterm=NONE
hi SignColumn guifg=#7f899b ctermfg=245 gui=NONE cterm=NONE
hi FoldColumn guifg=#7f899b ctermfg=245 gui=NONE cterm=NONE
hi Folded guifg=#566073 ctermfg=241 guibg=#e3e7ee ctermbg=254 gui=NONE cterm=NONE
hi VertSplit guifg=#dbe0e8 ctermfg=254 gui=NONE cterm=NONE
hi StatusLine guifg=#566073 ctermfg=241 guibg=#e3e7ee ctermbg=254 gui=NONE cterm=NONE
hi StatusLineNC guifg=#7f899b ctermfg=245 guibg=#e3e7ee ctermbg=254 gui=NONE cterm=NONE
hi! link StatusLineTerm StatusLine
hi! link StatusLineTermNC StatusLineNC
hi TabLine guifg=#7f899b ctermfg=245 guibg=#e3e7ee ctermbg=254 gui=NONE cterm=NONE
hi TabLineSel guifg=#272d37 ctermfg=236 guibg=#eef1f5 ctermbg=255 gui=bold cterm=bold
hi TabLineFill guibg=#f7f8fa ctermbg=231 gui=NONE cterm=NONE
hi ToolbarLine guibg=#e3e7ee ctermbg=254 gui=NONE cterm=NONE
hi ToolbarButton guifg=#272d37 ctermfg=236 guibg=#d2d8e2 ctermbg=253 gui=bold cterm=bold
hi Pmenu guifg=#363d4a ctermfg=237 guibg=#e3e7ee ctermbg=254 gui=NONE cterm=NONE
hi PmenuSel guibg=#d2d8e2 ctermbg=253 gui=bold cterm=bold
hi PmenuSbar guibg=#e3e7ee ctermbg=254 gui=NONE cterm=NONE
hi PmenuThumb guibg=#7f899b ctermbg=245 gui=NONE cterm=NONE
hi PmenuMatch guifg=#2e62c0 ctermfg=25 gui=bold cterm=bold
hi PmenuMatchSel guifg=#2e62c0 ctermfg=25 guibg=#d2d8e2 ctermbg=253 gui=bold cterm=bold
hi PmenuKind guifg=#7650c4 ctermfg=98 gui=NONE cterm=NONE
hi PmenuKindSel guifg=#7650c4 ctermfg=98 guibg=#d2d8e2 ctermbg=253 gui=NONE cterm=NONE
hi PmenuExtra guifg=#566073 ctermfg=241 gui=NONE cterm=NONE
hi PmenuExtraSel guifg=#566073 ctermfg=241 guibg=#d2d8e2 ctermbg=253 gui=NONE cterm=NONE
hi! link WildMenu PmenuSel
hi Visual guibg=#d2d8e2 ctermbg=253 gui=NONE cterm=NONE
hi! link VisualNOS Visual
hi Search guifg=#272d37 ctermfg=236 guibg=#d1cab2 ctermbg=187 gui=NONE cterm=NONE
hi CurSearch guifg=#eef1f5 ctermfg=255 guibg=#866405 ctermbg=94 gui=bold cterm=bold
hi! link IncSearch CurSearch
hi MatchParen guifg=#272d37 ctermfg=236 guibg=#d2d8e2 ctermbg=253 gui=bold cterm=bold
hi NonText guifg=#b1b8c4 ctermfg=250 gui=NONE cterm=NONE
hi EndOfBuffer guifg=#d2d8e2 ctermfg=253 gui=NONE cterm=NONE
hi SpecialKey guifg=#b1b8c4 ctermfg=250 gui=NONE cterm=NONE
hi Conceal guifg=#7f899b ctermfg=245 gui=NONE cterm=NONE
hi Directory guifg=#2e62c0 ctermfg=25 gui=NONE cterm=NONE
hi Title guifg=#2e62c0 ctermfg=25 gui=bold cterm=bold
hi Question guifg=#267b4f ctermfg=29 gui=NONE cterm=NONE
hi MoreMsg guifg=#267b4f ctermfg=29 gui=NONE cterm=NONE
hi ModeMsg guifg=#363d4a ctermfg=237 gui=bold cterm=bold
hi ErrorMsg guifg=#b83d63 ctermfg=131 gui=NONE cterm=NONE
hi WarningMsg guifg=#866405 ctermfg=94 gui=NONE cterm=NONE
hi QuickFixLine guibg=#d2d8e2 ctermbg=253 gui=bold cterm=bold
hi SpellBad guisp=#b83d63 gui=undercurl cterm=undercurl
hi SpellCap guisp=#866405 gui=undercurl cterm=undercurl
hi SpellRare guisp=#7650c4 gui=undercurl cterm=undercurl
hi SpellLocal guisp=#0f7480 gui=undercurl cterm=undercurl
hi DiffAdd guibg=#d0dfdc ctermbg=253 gui=NONE cterm=NONE
hi DiffChange guibg=#d7e0ef ctermbg=254 gui=NONE cterm=NONE
hi DiffDelete guifg=#b83d63 ctermfg=131 guibg=#e6d6df ctermbg=253 gui=NONE cterm=NONE
hi DiffText guibg=#b4c6e5 ctermbg=152 gui=NONE cterm=NONE
hi Added guifg=#267b4f ctermfg=29 gui=NONE cterm=NONE
hi Changed guifg=#2e62c0 ctermfg=25 gui=NONE cterm=NONE
hi Removed guifg=#b83d63 ctermfg=131 gui=NONE cterm=NONE
hi! link diffAdded Added
hi! link diffChanged Changed
hi! link diffRemoved Removed
hi diffFile guifg=#2e62c0 ctermfg=25 gui=bold cterm=bold
hi diffLine guifg=#7650c4 ctermfg=98 gui=NONE cterm=NONE
hi diffIndexLine guifg=#566073 ctermfg=241 gui=NONE cterm=NONE
hi Comment guifg=#7f899b ctermfg=245 gui=italic cterm=italic
hi Constant guifg=#a34396 ctermfg=132 gui=NONE cterm=NONE
hi String guifg=#267b4f ctermfg=29 gui=NONE cterm=NONE
hi Character guifg=#267b4f ctermfg=29 gui=NONE cterm=NONE
hi Number guifg=#a34396 ctermfg=132 gui=NONE cterm=NONE
hi Boolean guifg=#a34396 ctermfg=132 gui=NONE cterm=NONE
hi Float guifg=#a34396 ctermfg=132 gui=NONE cterm=NONE
hi Identifier guifg=#363d4a ctermfg=237 gui=NONE cterm=NONE
hi Function guifg=#2e62c0 ctermfg=25 gui=NONE cterm=NONE
hi Statement guifg=#7650c4 ctermfg=98 gui=NONE cterm=NONE
hi Conditional guifg=#b83d63 ctermfg=131 gui=bold cterm=bold
hi Repeat guifg=#866405 ctermfg=94 gui=NONE cterm=NONE
hi Label guifg=#866405 ctermfg=94 gui=NONE cterm=NONE
hi Operator guifg=#566073 ctermfg=241 gui=NONE cterm=NONE
hi Keyword guifg=#7650c4 ctermfg=98 gui=NONE cterm=NONE
hi Exception guifg=#b83d63 ctermfg=131 gui=NONE cterm=NONE
hi PreProc guifg=#866405 ctermfg=94 gui=NONE cterm=NONE
hi Include guifg=#7650c4 ctermfg=98 gui=NONE cterm=NONE
hi Define guifg=#7650c4 ctermfg=98 gui=NONE cterm=NONE
hi Macro guifg=#0f7480 ctermfg=30 gui=NONE cterm=NONE
hi PreCondit guifg=#866405 ctermfg=94 gui=NONE cterm=NONE
hi Type guifg=#866405 ctermfg=94 gui=NONE cterm=NONE
hi StorageClass guifg=#7650c4 ctermfg=98 gui=NONE cterm=NONE
hi Structure guifg=#866405 ctermfg=94 gui=NONE cterm=NONE
hi Typedef guifg=#866405 ctermfg=94 gui=NONE cterm=NONE
hi Special guifg=#0f7480 ctermfg=30 gui=NONE cterm=NONE
hi SpecialChar guifg=#0f7480 ctermfg=30 gui=NONE cterm=NONE
hi Tag guifg=#b83d63 ctermfg=131 gui=NONE cterm=NONE
hi Delimiter guifg=#5f7090 ctermfg=60 gui=NONE cterm=NONE
hi SpecialComment guifg=#566073 ctermfg=241 gui=italic cterm=italic
hi Debug guifg=#b83d63 ctermfg=131 gui=NONE cterm=NONE
hi Underlined gui=underline cterm=underline
hi Ignore guifg=#7f899b ctermfg=245 gui=NONE cterm=NONE
hi Error guifg=#b83d63 ctermfg=131 gui=NONE cterm=NONE
hi Todo guifg=#eef1f5 ctermfg=255 guibg=#866405 ctermbg=94 gui=bold cterm=bold

let g:terminal_ansi_colors = ['#363d4a', '#b83d63', '#267b4f', '#866405', '#2e62c0', '#7650c4', '#0f7480', '#7f899b', '#566073', '#90304d', '#1e603e', '#694e04', '#244c96', '#5c3e99', '#0c5a64', '#9ba3b2']
