-- Rime Glacier: Crisper accents with clear separation between every syntax role, on a lighter background.
-- https://github.com/w0x7y/rime
hl.config({
    general = {
        col = { active_border = "rgb(6eaaf0)", inactive_border = "rgb(414854)", nogroup_border = "rgb(414854)", nogroup_border_active = "rgb(ae94f0)" },
    },
    group = {
        col = { border_active = "rgb(6eaaf0)", border_inactive = "rgb(414854)", border_locked_active = "rgb(e3dc9e)", border_locked_inactive = "rgb(414854)" },
        groupbar = {
            text_color = "rgb(c5cedd)",
            text_color_inactive = "rgb(737e94)",
            col = { active = "rgb(6eaaf0)", inactive = "rgb(414854)", locked_active = "rgb(e3dc9e)", locked_inactive = "rgb(414854)" },
        },
    },
    misc = { background_color = "rgb(2a2f37)" },
})
