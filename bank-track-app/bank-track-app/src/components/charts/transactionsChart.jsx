import { Box } from '@chakra-ui/react';
import * as echarts from 'echarts';
import { useEffect } from 'react';


const TransactionsChart = ({ transactions, id }) => {

    const amountByDay = [...transactions]
        .sort((a, b) => new Date(a.booking_date) - new Date(b.booking_date))
        .reduce((acc, { booking_date, amount }) => {
            acc[booking_date] = (acc[booking_date] || 0) + parseFloat(amount);
            return acc;
        }, {});

    useEffect(() => {
        const chartDom = document.getElementById(id);
        const transactionsBar = echarts.init(chartDom, { renderer: 'svg' });
        const option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            xAxis: {
                type: 'category',
                data: Object.keys(amountByDay),
            },
            yAxis: {
                type: 'value',
            },
            series: [
                {
                    data: Object.values(amountByDay),
                    type: 'bar',
                    showBackground: true,
                    backgroundStyle: {
                        color: 'rgba(180, 180, 180, 0.2)'
                    }

                },
            ],
        };
        option && transactionsBar.setOption(option);

        return () => transactionsBar.dispose(); // Cleanup on component unmount
    }, [amountByDay, id]);

    return (
        <Box id={id} height='100%' width='100%' padding={2}></Box>
    );
};

export default TransactionsChart;
