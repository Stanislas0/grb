import React from 'react';
import { Badge, Select, Typography, Tooltip } from "antd";
import _ from "lodash";
import { Bar } from '@ant-design/charts';
import AttacksData from './attacks.json';
import ModelsData from './models.json';

const { Option } = Select;
const { Title, Paragraph } = Typography;

function renderSummaryCell(summary, type) {
    if (type === 'model') {
        if (summary === 'average') return 'Average Accuracy'
        else if (summary === '3-max') return 'Average 3-Max Accuracy'
        else if (summary === 'weighted') return 'Weighted Accuracy'
        else return summary
    } else {
        if (summary === 'no_attack') return 'W/O Attack'
        else if (summary === 'average') return 'Average Accuracy'
        else if (summary === '3-min') return 'Average 3-Min Accuracy'
        else if (summary === 'weighted') return 'Weighted Accuracy'
        else return summary
    }
}

function renderDrawer(title, refs) {
    return {
        'title': <Title level={4}>{title}</Title>,
        'description': <div className="description">
            <Title level={5}>References</Title>
            {refs.map((ref, idx) => <Paragraph key={idx}>[{idx+1}] {ref}</Paragraph>)}
        </div>
    }
}

function renderModelHeader(model_id, updateDrawer) {
    const model = ModelsData.find(model => model.id === model_id)
    const layer_norm = model_id.split('_').indexOf('ln') >= 0
    const adversarial_training = model_id.split('_').indexOf('at') >= 0
    const inner = <a onClick={() => updateDrawer(convertModelDataToDrawerData(model_id))}>{model.name}</a>
    return <div>
        {inner}
        {layer_norm && <Tooltip title="Layer Normalization"><span className="model-header-badge" style={{color: '#1890ff'}}>+LN</span></Tooltip>}
        {adversarial_training && <Tooltip title="Adversarial Training"><span className="model-header-badge" style={{color: '#ff9c6e'}}>+AT</span></Tooltip>}
    </div>
}

function convertAttackDataToDrawerData(attack_id) {
    const atk = AttacksData.find(atk => atk.id === attack_id)
    if (!atk) return undefined
    let refs = atk.refs || []
    if (atk.ref) refs.push(atk.ref)
    return renderDrawer(atk.id.toUpperCase(), refs)
}

function convertModelDataToDrawerData(model_id) {
    const model = ModelsData.find(model => model.id === model_id)
    if (!model) return undefined
    let refs = model.refs || []
    if (model.ref) refs.push(model.ref)
    return renderDrawer(model.id.split('_')[0].toUpperCase(), refs)
}

export function fetchLeaderboard() {
    return fetch(`https://raw.githubusercontent.com/Stanislas0/grb/results/leaderboard.json?token=ADK6VYJ3MU26KVKUN3DS6HDAYL2DC`)
        .then(resp => resp.json())
}

export function getTableColumns(configs, updateDrawer) {
    const {levels, models, modelsSummary} = configs
    const width = configs.width || 140
    return [{
        title: "Rank",
        // colSpan: 3,
        fixed: 'left',
        align: 'center',
        width: 100,
        render: (value, row, index) => {
            if (!row.isFirstRow) return {props: {rowSpan: 0, colSpan: 0}}
            else {
                if (row.rank === 0) return {children: <b>{renderSummaryCell(row.attack, 'attack')}</b>, props: {rowSpan: levels.length, colSpan: 2}}
                else return {children: <b>{row.rank}</b>, props: {rowSpan: levels.length, colSpan: 1}}
            }
        }
    }, {
        title: "Attack",
        // colSpan: 0,
        fixed: 'left',
        align: 'center',
        width: 100,
        render: (value, row, index) => {
            if (!row.isFirstRow) return {props: {rowSpan: 0, colSpan: 0}}
            else {
                if (row.rank === 0) return {props: {rowSpan: 0, colSpan: 0}}
                else return {
                    children: <a className="table-attack-header" onClick={() => updateDrawer(convertAttackDataToDrawerData(row.attack))}>
                        <b>{row.attack.toUpperCase()}</b>
                    </a>,
                    props: {rowSpan: levels.length, colSpan: 1}}
            }
        }
    }, {
        title: "Difficulty",
        // colSpan: 0,
        fixed: 'left',
        align: 'center',
        width: 100,
        render: (value, row, index) => {
            return {children: <b>{_.capitalize(row.level)}</b>, props: {rowSpan: 1, colSpan: 1}}
            // return {children: <a href={`#level-chart:${row.level}`}>{_.capitalize(row.level)}</a>, props: {rowSpan: 1, colSpan: 1}}
        }
    }, {
        title: "Models",
        children: models.map(model => {
            return {
                title: renderModelHeader(model, updateDrawer),
                dataIndex: model,
                key: model,
                align: 'center',
                width,
                render: (value, row, index) => {
                    return row.bold.indexOf(model) >= 0 ? <b>{value}</b> : value
                }
            }
        })
    }].concat(modelsSummary.map(model => {
        return {
            title: renderSummaryCell(model, 'model'),
            dataIndex: model,
            key: model,
            align: 'center',
            width,
            render: (value, row, index) => {
                return row.bold.indexOf(model) >= 0 ? <b>{value}</b> : value
            }
        }
    }))
}

export function getTableItems(data, configs) {
    const {attacks, attacksSummary, models, modelsSummary, levels} = configs
    const bestModelScore = {}
    attacksSummary.forEach(attackSummary => levels.forEach(level => {
        let best = 0
        models.forEach(model => best = Math.max(best, data[attackSummary][level][model]))
        if (!bestModelScore[attackSummary]) bestModelScore[attackSummary] = {}
        bestModelScore[attackSummary][level] = best
    }))
    const bestAttackScore = {}
    levels.forEach(level => modelsSummary.forEach(modelSummary => {
        let best = 1
        attacks.forEach(attack => best = Math.min(best, data[attack][level][modelSummary]))
        if (!bestAttackScore[level]) bestAttackScore[level] = {}
        bestAttackScore[level][modelSummary] = best
    }))

    const items = _.flatMap(attacks.concat(attacksSummary), atk => {
        return levels.map((level, lid) => {
            let item = {
                'attack': atk,
                'rank': attacks.indexOf(atk) + 1,
                'level': level,
                'isFirstRow': lid === 0,
                'bold': []
            }
            models.concat(modelsSummary).forEach(m => {
                if (data[atk][level][m]) item[m] = data[atk][level][m].toFixed(4)
                else item[m] = '-'
                if (attacksSummary.indexOf(atk) >= 0 && models.indexOf(m) >= 0) {
                    if (data[atk][level][m] === bestModelScore[atk][level]) item['bold'].push(m)
                } else if (attacks.indexOf(atk) >= 0 && modelsSummary.indexOf(m) >= 0) {
                    if (data[atk][level][m] === bestAttackScore[level][m]) item['bold'].push(m)
                }
            })
            return item
        })
    })
    return items
}

export function getTableSelection(key, leaderboard, configs, setConfigs) {
    return <div className="table-config">
        <div style={{width: 100}}><Title level={5}>{(key === 'levels') ? 'Difficulty' : _.capitalize(key)}:</Title></div>
        <div className="selection-box">
        {leaderboard[key] && <Select mode="multiple" value={configs[key]} onChange={(value) => {
            const newConfigs = _.clone(configs)
            newConfigs[key] = value.sort((a, b) => leaderboard[key].indexOf(a) - leaderboard[key].indexOf(b))
            setConfigs(newConfigs)
        }} style={{width: '100%', marginLeft: 10}}>
            {leaderboard[key].map(v => <Option key={v}>{
                (key === 'attacks') ? v.toUpperCase() :
                (key === 'levels') ? _.capitalize(v) : v}</Option>)}
        </Select>}
        </div>
    </div>
}

export function getChart(data, level, configs) {
    const {attacks, modelsSummary} = configs
    let barData = _.flatMap(attacks, atk => modelsSummary.map(modelSummary => {
        return { label: atk.toUpperCase(), type: modelSummary, value: parseFloat(data[atk][level][modelSummary].toFixed(4)) }
    }))
    return <Bar data={barData} isGroup xField="value" yField="label" seriesField="type" marginRatio={0.1}
        label={{
            position: "middle",
            layout: [
                { type: 'interval-adjust-position' },
                { type: 'interval-hide-overlap' },
                { type: 'adjust-color' },
            ]
    }}/>
}