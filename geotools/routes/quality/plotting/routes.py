import matplotlib.pyplot as plt


def plot_test(test_result, kwargs=None):
    plt.title(f"{test_result.identifier}")
    for provider, result in test_result.routes.items():
        plt.scatter(
            *zip(*result.route.geometry.to_lng_lat_tuples()),
            label=provider,
            **kwargs or {},
        )

    plt.legend()
    plt.tight_layout()

    for metric, score in test_result.metrics.items():
        plt.text(1.01, 0.9, f"{metric}: {score}")
