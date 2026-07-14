const DEFAULT_THEME = {
    title: "Личный профиль",
    color: "#8B78F3",
    softColor: "#EFECFF",
};

const ARCHETYPE_GROUPS = [
    {
        title: "Аналитики",
        color: "#C92CA8",
        softColor: "#FBE9F7",
        types: ["INTJ", "INTP", "ENTJ", "ENTP"],
    },
    {
        title: "Дипломаты",
        color: "#BADC6A",
        softColor: "#F3F9DF",
        types: ["INFJ", "INFP", "ENFJ", "ENFP"],
    },
    {
        title: "Хранители",
        color: "#8B78F3",
        softColor: "#EFECFF",
        types: ["ISTJ", "ISFJ", "ESTJ", "ESFJ"],
    },
    {
        title: "Искатели",
        color: "#F7C054",
        softColor: "#FFF4DE",
        types: ["ISTP", "ISFP", "ESTP", "ESFP"],
    },
];

export function getArchetypeTheme(type) {
    return ARCHETYPE_GROUPS.find((group) => group.types.includes(type)) || DEFAULT_THEME;
}
