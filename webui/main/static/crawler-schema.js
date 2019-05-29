var attrSchema = {
    type: 'array',
    minLength: 1,
    items: {
        type: 'object',
        properties: {
            method: {
                type: 'string',
                default: 'xpath',
                // enum: ['xpath', 'css', 'attr', 'value', 're', 're_first', 'get_attr']
                enum: ['extract', 'set_value', 'get_browser_count', 'get_content', 'strip', 'list2str', 'padtime_for_caogen', 'filter_tags', 'get_hits_for_clubchina', 'set_default_source_military', 'date_transform', 'cut_from_tail', 'replace', 're_first', 'xpath', 'extract_first', 'css', 'set_default_source_chinadaily', 'set_default_time', 'set_default_time_military', 'get_bbs_info', 'set_default_author_chinadaily', 'get_time', 'set_default_values', 'get_attr','sub']
            },
            args: {
                type: 'array',
                default: [],
                items: {
                    type: ['string','number']
                }
            }
        },
        required: ['method']
    }
}

var crawlerSchema = {
    $schema: "http://json-schema.org/schema#",
    title: '爬虫schema',
    type: "object",
    // additionalProperties: false,
    displayProperty: "website",
    properties: {
        website: {
            type: 'string',
            description: '网站',
            title: '网站'
        },
        index: {
            type: 'string',
            description: '主页',
            title: '主页'
        },
        type: {
            type: 'string',
            enum: ['门户', '教育', '视频', 'wrap'],
            title: '网站类型',
            description: '网站类型'
        },
        spider: {
            type: "string",
            //固定值
            enum: ['universal'],
            description: '爬虫类',
            title: '爬虫类'
        },
        settings: {
            type: "object",
            additionalProperties: true,
            description: '设置',
            title: '设置',
            properties: {
                USER_AGENT: {
                    type: "string",
                    default: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"
                    // enum: ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"]
                },
                ITEM_PIPELINES: {
                    type: "object",
                    additionalProperties: {
                        type: "number"
                    }
                }
            }
        },
        splash: {
            type: 'object',
            additionalProperties: true,
            properties: {}
        },
        start_urls: {
            title: "起始链接",
            type: 'object',
            items: {
                type: "string"
            }
        },
        allowed_domains: {
            type: "array",
            description: "允许的域名",
            title: "允许的域名",
            items: {
                type: 'string'
            }
        },
        rules: {
            type: 'string'
        },
        item: {
            type: 'object',
            displayProperties: "class",
            properties: {
                table: {
                    description: "数据库表",
                    type: "string"
                },
                class: {
                    description: '对应Item类',
                    type: 'string'
                },
                loader: {
                    type: 'string'
                },
                attrs: {
                    type: 'object',
                    additionalProperties: attrSchema,
                    properties: {
                        title: attrSchema,
                        url: attrSchema,
                        content: attrSchema,
                        publish_time: attrSchema,
                        source: attrSchema,
                        website: attrSchema,
                        author: attrSchema
                    }
                }
            }
        }
    }
}
//node crawler-schema.js > crawler-schema.json
console.log(JSON.stringify(crawlerSchema))