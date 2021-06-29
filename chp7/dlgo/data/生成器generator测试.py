
from dlgo.data.parallel_processor import  GoDataProcessor  # 采用并行处理


if __name__ == '__main__':
    processor = GoDataProcessor()
    generator = processor.load_go_data('test', 100, use_generator=True)  # 生成一个 test_sample.py文件
    print(generator.get_num_samples())

    generator = generator.generate(batch_size=10)
    X, y = next(generator)

    print(X)
    print("-------------------")
    print(y)
